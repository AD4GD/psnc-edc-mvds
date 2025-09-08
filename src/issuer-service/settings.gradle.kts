
rootProject.name = "edc-identity-hub"

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

include("launchers:dcp")
include("extensions:did-example-resolver")
include("extensions:superuser-seed")