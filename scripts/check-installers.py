#!/usr/bin/env python3
"""Offline installer regressions. Extracts shell sections; never runs full installers.
Usage: python3 scripts/check-installers.py [SOURCE_ROOT]
Requires Python 3, /bin/sh, patch, tar and standard coreutils. No network.
"""
import hashlib, io, json, os, pathlib, shlex, subprocess, sys, tarfile, tempfile
repo = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv)>1 else pathlib.Path(__file__).resolve().parents[1]
results = []
def check(name, condition, detail=''):
    results.append(dict(case=name, passed=bool(condition), detail=detail))
    if not condition: raise AssertionError((name, detail))
def shell(code, env=None):
    return subprocess.run(['/bin/sh', '-c', code], text=True, capture_output=True, env=env)
def q(p): return shlex.quote(str(p))
patch = (repo/'patches/wlroots-0.18-parent-keymap.patch').read_text()
# Reconstruct only the original hunk context. This is a synthetic patch fixture,
# not a downloaded wlroots tree or a callback compilation test.
original = ''.join(line[1:]+'\n' for line in patch.splitlines()
                   if line.startswith((' ', '-')) and not line.startswith('---'))
with tempfile.TemporaryDirectory(prefix='desk-audit-') as directory:
    t = pathlib.Path(directory)
    root = t/'project'; (root/'scripts').mkdir(parents=True); (root/'patches').mkdir()
    helper = root/'scripts/wlroots-keymap.sh'
    helper.write_bytes((repo/'scripts/wlroots-keymap.sh').read_bytes())
    patchfile = root/'patches/wlroots-0.18-parent-keymap.patch'; patchfile.write_text(patch)
    src = t/'wlroots-0.18.3'; (src/'backend/wayland').mkdir(parents=True)
    (src/'backend/wayland/seat.c').write_text(original)
    r = shell(f'sh {q(helper)} {q(src)}')
    check('helper applies to synthetic original context', r.returncode == 0, r.stdout+r.stderr)
    r = shell(f'sh {q(helper)} {q(src)}')
    check('helper refuses repeat application', r.returncode != 0)
    fp = shell(f'sh {q(helper)} --fingerprint').stdout.strip()
    check('fingerprint equals patch SHA256', fp == hashlib.sha256(patch.encode()).hexdigest())
    patchfile.write_text(patch+'\n')
    check('patch content changes fingerprint', shell(f'sh {q(helper)} --fingerprint').stdout.strip()!=fp)
    patchfile.write_text(patch)
    private=t/'validator-prefix'; pcdir=private/'lib/pkgconfig'; pcdir.mkdir(parents=True)
    (pcdir/'wlroots-0.18.pc').touch(); lib=private/'lib/libwlroots-0.18.so'; lib.touch()
    tools=t/'validator-bin'; tools.mkdir(); pc=tools/'pkg-config'
    pc.write_text('#!/bin/sh\ncase "$1" in --variable=pcfiledir) echo "$PCDIR";; --variable=libdir) echo "$LIBDIR";; --exact-version=*) [ "$VERSION_OK" = yes ];; esac\n'); pc.chmod(0o755)
    env=os.environ.copy(); env.update(PATH=str(tools)+':'+env['PATH'],PCDIR=str(pcdir),LIBDIR=str(private/'lib'),VERSION_OK='yes')
    def validate(): return shell(f'sh {q(helper)} --check-installed {q(private)} 0.18.3',env).returncode==0
    check('validator accepts private metadata and library', validate())
    metadata=pcdir/'wlroots-0.18.pc'; metadata.unlink()
    check('validator rejects missing metadata despite successful pkg-config', not validate()); metadata.touch()
    env['PCDIR']=str(t); check('validator rejects external metadata', not validate()); env['PCDIR']=str(pcdir)
    env['LIBDIR']=str(t); check('validator rejects external libdir', not validate()); env['LIBDIR']=str(private/'lib')
    env['VERSION_OK']='no'; check('validator rejects wrong version', not validate()); env['VERSION_OK']='yes'
    lib.unlink(); check('validator rejects missing library', not validate())
    outside=t/'outside.so'; outside.touch(); lib.symlink_to(outside)
    check('validator rejects library symlink outside prefix', not validate())
    lib.unlink(); target=private/'lib/libwlroots-0.18.so.0'; target.touch(); lib.symlink_to(target.name)
    check('validator accepts versioned library symlink inside prefix', validate())
    for distro in ['arch', 'ubuntu']:
        text = (repo/f'scripts/install_{distro}.sh').read_text()
        check(f'{distro}: shell syntax', shell(f'sh -n {q(repo/f"scripts/install_{distro}.sh")}').returncode==0)
        # Execute the actual integrity guard, ending before distribution tools.
        guard = text[text.index('if [ -z "${DESK_SUMS_CHECKED:-}" ]'):text.index('command -v pacman' if distro=='arch' else 'command -v apt-get')]
        r = shell('set -eu\nroot='+q(repo)+'\ndie() { echo "$*"; exit 1; }; say() { :; };\n'+guard)
        check(f'{distro}: tracked manifest accepts checkout', r.returncode==0)
        block = text[text.index('pcpath="$wlr/lib/pkgconfig'):text.index('# -- 3. build')]
        for case in ['fresh','cached','changed','missing-patch','patch-failure','setup-failure','compile-failure','install-failure','missing-private-pc']:
            c=t/(distro+'-'+case); c.mkdir(); deps=c/'deps'; deps.mkdir(); tmp=c/'tmp'; tmp.mkdir()
            wlr=c/'prefix'; stamp=wlr/'share/desk-wlroots/built'; stamp.parent.mkdir(parents=True)
            bindir=c/'bin'; bindir.mkdir(); log=c/'calls'
            # A synthetic archive exercises real checksum verification, unpacking,
            # patch invocation and stamp writes. Meson and pkg-config are stubs.
            archive=deps/'wlroots-0.18.3.tar.gz'
            fixture=original if case!='patch-failure' else 'not matching patch\n'
            with tarfile.open(archive,'w:gz') as tf:
                b=fixture.encode(); info=tarfile.TarInfo('wlroots-0.18.3/backend/wayland/seat.c'); info.size=len(b); tf.addfile(info,io.BytesIO(b))
            digest=hashlib.sha256(archive.read_bytes()).hexdigest()
            todo='wlroots 0.18.3\nnested-keymap '+fp
            if case in ['cached','missing-private-pc']: stamp.write_text(todo+'\n')
            privatepc=wlr/'lib/pkgconfig'; privatepc.mkdir(parents=True)
            if case!='missing-private-pc':
                (privatepc/'wlroots-0.18.pc').touch()
                (wlr/'lib/libwlroots-0.18.so').touch()
            if case=='changed': stamp.write_text('wlroots 0.18.3\nnested-keymap old\n')
            if case=='missing-patch': patchfile.unlink()
            pc=bindir/'pkg-config'
            pc.write_text('#!/bin/sh\ncase "$1" in --variable=have_xwayland) echo true;; --variable=pcfiledir) echo "$PCDIR";; --variable=libdir) echo "$LIBDIR";; esac; exit 0\n')
            pc.chmod(0o755)
            meson=bindir/'meson'
            meson.write_text('#!/bin/sh\necho "meson $*" >> "$CALLS"\ncase "$CASE:$1" in setup-failure:setup|compile-failure:compile|install-failure:install) exit 9;; esac\n')
            meson.write_text(meson.read_text()+'if [ "$1" = install ]; then mkdir -p "$PRIVATE/lib/pkgconfig"; touch "$PRIVATE/lib/pkgconfig/wlroots-0.18.pc" "$PRIVATE/lib/libwlroots-0.18.so"; fi\n')
            meson.chmod(0o755)
            pre='set -eu\n'+ '\n'.join(f'{k}={q(v)}' for k,v in dict(root=root,wlr=wlr,deps=deps,tmp=tmp,stamp=stamp,wlroots='source',SOURCES=f'wlroots|wlroots-0.18|0.18.3|0.18.3|https://invalid.test/wlroots-0.18.3.tar.gz|{digest}|-Dexamples=false').items())+'\n'
            pre+='''say() { echo "$*"; }; step() { :; }; die() { echo "$*" >&2; exit 1; }
as_builder() { "$@"; }; as_root() { "$@"; }
curl() { echo FORBIDDEN_NETWORK >&2; exit 99; }
'''
            env=os.environ.copy(); env.update(PATH=str(bindir)+':'+env['PATH'],CALLS=str(log),CASE=case,PRIVATE=str(wlr),PCDIR=str(privatepc),LIBDIR=str(wlr/'lib'))
            r=shell(pre+block,env)
            calls=log.read_text() if log.exists() else ''
            if case in ['fresh','changed','missing-private-pc']:
                check(f'{distro}: {case} patches, builds and stamps',r.returncode==0 and 'meson setup' in calls and stamp.read_text().strip()==todo, r.stdout+r.stderr+calls)
            elif case == 'cached':
                check(f'{distro}: {case} takes cache hit',r.returncode==0 and not calls and 'kept' in r.stdout,
                      r.stdout+r.stderr)
            elif case=='missing-patch':
                check(f'{distro}: fingerprint failure stops before unpacking',r.returncode!=0 and 'building wlroots' not in r.stdout and 'could not fetch' not in r.stderr and not (deps/'wlroots-0.18.3').exists(),r.stderr)
                # Assignment preserves substitution failure status under set -e.
                patchfile.write_text(patch)
            else:
                check(f'{distro}: {case} stops without stamp',r.returncode!=0 and not stamp.exists(),r.stderr)
                if case=='patch-failure': check(f'{distro}: patch failure precedes Meson', not calls)
        # Dependency selection: execute actual selection snippets using stubs.
        start=text.index('stamp="$wlr/share/desk-wlroots/built"')
        end=text.index('if installed wlroots0.18;',start+len('stamp="$wlr/share/desk-wlroots/built"')) if distro=='arch' else text.index('missing=0',start)
        # Arch includes two identical condition openers; select through first fi.
        selection=text[start:text.index('\nfi',start)+3] if distro=='arch' else text[start:end]
        for installed,existing,known,expected in [(1,1,1,'pacman' if distro=='arch' else 'apt'),(0,1,1,'source'),(0,0,1,'pacman' if distro=='arch' else 'unknown'),(0,0,0,'source' if distro=='arch' else 'unknown')]:
            w=t/f'select-{distro}-{installed}{existing}{known}'; s=w/'share/desk-wlroots/built'; s.parent.mkdir(parents=True)
            if existing:s.touch()
            r=shell('set -eu\nwlr='+q(w)+f'\ninstalled() {{ return {0 if installed else 1}; }}; known() {{ return {0 if known else 1}; }};\n'+selection+'\necho "$wlroots"')
            check(f'{distro}: selection installed={installed} stamp={existing} known={known}',r.returncode==0 and r.stdout.strip()==expected,r.stdout+r.stderr)
        if distro=='ubuntu':
            late=text[text.index('if [ "$wlroots" = unknown ]; then'):text.index('if [ "$wlroots" = apt ]; then')]
            for known in [0,1]:
                r=shell(f'set -eu; wlroots=unknown; known() {{ return {0 if known else 1}; }};\n'+late+'\necho "$wlroots"')
                check(f'ubuntu: refreshed selection known={known}',r.stdout.strip()==('apt' if known else 'source'))
print(json.dumps(results,indent=2))
print(f'PASS: {len(results)} offline audit assertions')
