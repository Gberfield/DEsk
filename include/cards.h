#pragma once

#include <stdbool.h>
#include <stddef.h>

/* The firmware's framebuffer beside a real GPU (cards.c).
 *
 * Which of the machine's DRM cards wlroots should take, when it should not
 * take them all: sys is /sys/class/drm, udev /run/udev/data (which seat
 * each card is on), seat ours. True with the list for WLR_DRM_DEVICES in
 * list (the card the firmware booted on first) and the cards left out, for
 * the log, in why; false to leave wlroots to it. */
bool desk_cards_pick(const char *sys, const char *udev, const char *seat, char *list, size_t n,
	char *why, size_t wn);
