* We wanna get prebuilt binary packages for bleeding edge software.
    * Using bleeding edge software helps us get known about bugs before they are standardized as features.

* In order to get the bleeding edge software we create the infrastructure allowing us to build packages easily.
    * This is not a build system. Instead it uses other build systems. But build systems can reuse our code.
    * We need a flexible programming language in order to create build pipelines. More flexible than bash and make. To be honest, as languages they are completely unusable, we don't want to touch them. So we use python. We don't want to touch any tools built around GNU Make and bash, such as `debhelper`
    * Some build systems require an archive. It is dirty. Some of them even have glitches unpacking it.

* If upstream developers don't build them, we often can setup CI to build them.
    * But we should to send PRs to upstream devs in order to offload us.

* We wanna build as little as possible.
    * All the dependencies available as binary packages should be used as binary packages. If there is no binary packages for dependencies, we probably can setup CI to build them.
    * If building is infeasible, probably we can repackage already built binary distributions that are not packages.

* We trust the infrastructure enough to use it to build our packages, but we distrust it enough to have the builds reproducible.
    * Don't trust the signatures made by keys uploaded on CI. So we should build locally as much as we can.
    * So our pipelines should work locally well and give the same binaries.

* Our packages should be usable without adding a repo
    * So we sign each package.
