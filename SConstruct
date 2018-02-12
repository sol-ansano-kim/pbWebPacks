import os
env = Environment()


install_google_map = True
install_slack = True
dist_path = os.path.abspath(ARGUMENTS.get("dist", "release"))


try:
    install_google_map = int(ARGUMENTS.get("install-googlemap", "1")) != 0
    install_slack = int(ARGUMENTS.get("install-slack", "1")) != 0
except:
    install_google_map = True
    install_slack = True


env.Install(os.path.join(dist_path, "pbWebPacks"), Glob("web/*.py"))
env.Install(os.path.join(dist_path, "pbWebPacks"), Glob("web/*.config"))


if install_google_map:
    env.Install(os.path.join(dist_path, "pbWebPacks"), Glob("googleMap/*.py"))
    env.Install(os.path.join(dist_path, "pbWebPacks"), Glob("googleMap/*.config"))


if install_slack:
    env.Install(os.path.join(dist_path, "pbWebPacks"), Glob("slack/*.py"))
    env.Install(os.path.join(dist_path, "pbWebPacks"), Glob("slack/*.config"))
