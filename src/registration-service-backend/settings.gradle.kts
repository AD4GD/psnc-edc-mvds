rootProject.name = "registration-service"

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
        maven {
            url = uri("https://oss.sonatype.org/content/repositories/snapshots/")
        }
        mavenCentral()
        mavenLocal()
    }
}

include(":core:registration-service")
include(":core:identity-provider-client")
include(":core:federated-catalog-client")
include(":core:registration-service-client")
include(":extensions:registration-service-api")
include(":extensions:store:sql:participant-store-sql")
include(":launcher")
include(":registration-service-cli")
include(":spi:registration-service-spi")
include(":spi:registration-service-store-spi")
include(":system-tests")
include(":system-tests:launchers:participant")
include(":version-catalog")
