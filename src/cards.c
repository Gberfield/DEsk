/* The firmware's framebuffer beside a real GPU.
 *
 * Before any GPU driver is in, the kernel puts up a screen of its own on
 * the framebuffer the firmware left: simpledrm (and on newer kernels
 * efidrm, vesadrm; ofdrm on Open Firmware). A GPU's driver takes it over
 * when it comes -- but one that does not (NVIDIA's, without
 * nvidia_drm.fbdev=1) leaves both, and wlroots 0.18 takes every card there
 * is, the first it finds as the one it renders with, unless the firmware
 * booted on another (boot_vga). The firmware's card has no GPU behind it:
 * that was a desk drawn on the processor, in 2D, on a screen called
 * Unknown-1 -- the laptop's own panel, the firmware's way -- with the real
 * panel beside it as a second screen (Darkhawk's, on v0.1.3).
 *
 * So when one is there with a real card that has screens of its own, the
 * list wlroots takes (WLR_DRM_DEVICES) is the real cards: the one the
 * firmware booted on first, then the rest, as wlroots orders them itself,
 * and only those on our seat, as it would. Only sysfs is read (and udev's
 * note of each card's seat): nothing is opened, so this can run before
 * there is a session to open anything with. */

#include "cards.h"

#include <dirent.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define CARDS_MAX 16

struct card {
	int num;
	bool firmware, screens, boot, away;
	char driver[64];
};

/* the platform devices firmware framebuffers are, by their drivers' names:
 * simpledrm's and simplefb's, efidrm's and efifb's, vesadrm's and vesafb's,
 * ofdrm's */
static bool firmware_name(const char *s)
{
	static const char *const FW[] = { "simple-framebuffer", "efi-framebuffer",
		"vesa-framebuffer", "of-display" };
	for (size_t i = 0; i < sizeof FW / sizeof FW[0]; i++) {
		size_t k = strlen(FW[i]);
		if (!strncmp(s, FW[i], k) && (s[k] == '\0' || s[k] == '.')) {
			return true;
		}
	}
	return false;
}

/* the last part of where a link points */
static void link_name(const char *path, char *out, size_t n)
{
	char buf[PATH_MAX];
	ssize_t k = readlink(path, buf, sizeof buf - 1);
	out[0] = '\0';
	if (k <= 0) {
		return;
	}
	buf[k] = '\0';
	const char *b = strrchr(buf, '/');
	b = b ? b + 1 : buf;
	size_t len = strlen(b) < n ? strlen(b) : n - 1;
	memcpy(out, b, len);
	out[len] = '\0';
}

static bool first_line(const char *path, char *out, size_t n)
{
	FILE *f = fopen(path, "r");
	if (!f) {
		return false;
	}
	bool ok = fgets(out, (int)n, f) != NULL;
	fclose(f);
	if (ok) {
		out[strcspn(out, "\n")] = '\0';
	}
	return ok;
}

/* whether udev put the card on a seat other than ours (none said: seat0,
 * as wlroots has it) */
static bool on_other_seat(const char *sys, const char *udev, int num, const char *seat)
{
	char p[PATH_MAX], dev[32], line[256];
	bool other = strcmp(seat, "seat0") != 0;
	snprintf(p, sizeof p, "%s/card%d/dev", sys, num);
	if (!first_line(p, dev, sizeof dev)) {
		return other;
	}
	snprintf(p, sizeof p, "%s/c%s", udev, dev);
	FILE *f = fopen(p, "r");
	if (!f) {
		return other;
	}
	while (fgets(line, sizeof line, f)) {
		if (!strncmp(line, "E:ID_SEAT=", 10)) {
			line[strcspn(line, "\n")] = '\0';
			other = strcmp(line + 10, seat) != 0;
		}
	}
	fclose(f);
	return other;
}

static int by_num(const void *a, const void *b)
{
	return ((const struct card *)a)->num - ((const struct card *)b)->num;
}

bool desk_cards_pick(const char *sys, const char *udev, const char *seat, char *list, size_t n,
	char *why, size_t wn)
{
	struct card cards[CARDS_MAX];
	int nc = 0;
	DIR *d = opendir(sys);
	if (!d) {
		return false;
	}
	struct dirent *e;
	while ((e = readdir(d)) && nc < CARDS_MAX) {
		int num, len = 0;
		if (sscanf(e->d_name, "card%d%n", &num, &len) == 1 && len > 0 && e->d_name[len] == '\0') {
			memset(&cards[nc], 0, sizeof cards[nc]);
			cards[nc++].num = num;
		}
	}
	/* and its screens: card0-eDP-1, card0-HDMI-A-1... */
	rewinddir(d);
	while ((e = readdir(d))) {
		int num, len = 0;
		if (sscanf(e->d_name, "card%d-%n", &num, &len) == 1 && len > 0) {
			for (int i = 0; i < nc; i++) {
				cards[i].screens |= cards[i].num == num;
			}
		}
	}
	closedir(d);
	qsort(cards, (size_t)nc, sizeof cards[0], by_num);

	bool firmware = false, real = false;
	for (int i = 0; i < nc; i++) {
		struct card *c = &cards[i];
		char p[PATH_MAX], v[16];
		snprintf(p, sizeof p, "%s/card%d/device/driver", sys, c->num);
		link_name(p, c->driver, sizeof c->driver);
		char dev[64];
		snprintf(p, sizeof p, "%s/card%d/device", sys, c->num);
		link_name(p, dev, sizeof dev);
		c->firmware = firmware_name(c->driver) || (!c->driver[0] && firmware_name(dev));
		snprintf(p, sizeof p, "%s/card%d/device/boot_vga", sys, c->num);
		c->boot = first_line(p, v, sizeof v) && !strcmp(v, "1");
		c->away = on_other_seat(sys, udev, c->num, seat);
		firmware |= c->firmware && !c->away;
		real |= !c->firmware && c->screens && !c->away;
	}
	if (!firmware || !real) {
		return false;
	}
	list[0] = why[0] = '\0';
	size_t at = 0, wat = 0;
	for (int pass = 0; pass < 2; pass++) {
		for (int i = 0; i < nc; i++) {
			const struct card *c = &cards[i];
			if (c->firmware || !c->screens || c->away || c->boot != (pass == 0)) {
				continue;
			}
			int k = snprintf(list + at, n - at, "%s/dev/dri/card%d", at ? ":" : "", c->num);
			if (k < 0 || (size_t)k >= n - at) {
				return false;
			}
			at += (size_t)k;
		}
	}
	for (int i = 0; i < nc; i++) {
		const struct card *c = &cards[i];
		if (c->firmware && !c->away && wat < wn) {
			int k = snprintf(why + wat, wn - wat, "%scard%d (%s)", wat ? ", " : "", c->num,
				c->driver[0] ? c->driver : "the firmware's");
			wat += k > 0 ? (size_t)k : 0;
		}
	}
	return true;
}
