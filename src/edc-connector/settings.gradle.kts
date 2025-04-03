
rootProject.name = "AD4GD-Demo"

pluginManagement {
    repositories {
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositories {
        mavenCentral()
        mavenLocal()
    }
}

include("core:base")
include("launchers:daps")
include("launchers:no-daps")
include("extensions:connector-persistence")
include("extensions:policy-engine")
