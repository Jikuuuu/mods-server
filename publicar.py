"""Lee la carpeta 'mods' y crea el archivo manifest.json que usa el launcher."""
import hashlib
import json
import sys
from pathlib import Path

# ===================== CAMBIA ESTO SI HACE FALTA =====================
SERVER_IP = "sv19.minehost.pro"
SERVER_PORT = 25567
MINECRAFT = "1.19.2"
FORGE = "auto"          # "auto" = la ultima de 1.19.2. Si tu server usa una exacta: "1.19.2-43.2.23"

# Solo cuando saques un .exe NUEVO del launcher (sino dejalo vacio):
LAUNCHER_VERSION = ""   # ej: "0.2.0"  (tiene que ser mayor a la que tienen tus amigos)
LAUNCHER_URL = ""       # link directo al Launcher.exe nuevo (GitHub > Releases)
# =====================================================================

here = Path(__file__).resolve().parent
mods_dir = here / "mods"
manifest_path = here / "manifest.json"


def sha1(p):
    h = hashlib.sha1()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1024 * 1024), b""):
            h.update(c)
    return h.hexdigest()


if not mods_dir.is_dir():
    print("No encuentro la carpeta 'mods' al lado de este archivo.")
    sys.exit(1)

jars = sorted(mods_dir.glob("*.jar"), key=lambda p: p.name.lower())
if not jars:
    print("La carpeta 'mods' no tiene ningun .jar.")
    sys.exit(1)

files = []
for p in jars:
    size = p.stat().st_size
    if size > 99 * 1024 * 1024:
        print(f"OJO: {p.name} pesa mas de 99 MB y GitHub no lo acepta.")
    files.append({"path": f"mods/{p.name}", "sha1": sha1(p), "size": size})

old = {}
if manifest_path.exists():
    try:
        old = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        old = {}
old_files = {f["path"]: f["sha1"] for f in old.get("files", [])}
new_files = {f["path"]: f["sha1"] for f in files}

added = [p for p in new_files if p not in old_files]
removed = [p for p in old_files if p not in new_files]
changed = [p for p in new_files if p in old_files and old_files[p] != new_files[p]]

version = int(old.get("version", 0))
if added or removed or changed or not old:
    version += 1

manifest = {
    "version": version,
    "minecraft": MINECRAFT,
    "forge": FORGE,
    "server": SERVER_IP,
    "port": SERVER_PORT,
    "files": files,
}
if LAUNCHER_VERSION and LAUNCHER_URL:
    manifest["launcher"] = {"version": LAUNCHER_VERSION, "url": LAUNCHER_URL}

manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

print(f"Listo. manifest.json actualizado (version {version}) con {len(files)} mods.")
for label, lst in (("Agregados", added), ("Quitados", removed), ("Cambiados", changed)):
    if lst and old:
        print(f"  {label}: " + ", ".join(Path(x).name for x in lst))
print("\nAhora abri GitHub Desktop, escribi un titulo y toca 'Commit' y despues 'Push origin'.")
