rootProject.name = "federated-catalog"

include(":core:base")
include(":launchers:daps")
include(":launchers:no-daps")
include(":extensions:target-node-directory-sql")
include(":extensions:catalog-node-static-resolver")

// this is needed to have access to snapshot builds of plugins
pluginManagement {
    repositories {
        mavenLocal()
        maven {
            url = uri("https://oss.sonatype.org/content/repositories/snapshots/")
        }
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositories {
        mavenLocal()
        maven {
            url = uri("https://oss.sonatype.org/content/repositories/snapshots/")
        }
        mavenCentral()
    }
}
