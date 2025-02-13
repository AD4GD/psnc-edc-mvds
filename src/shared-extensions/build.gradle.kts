plugins {
    java
    `maven-publish`
}

group = "com.psnc.mvds"
version = "1.0.0"

subprojects {
    apply(plugin = "java-library")
    apply(plugin = "maven-publish")

    repositories {
        mavenLocal()
        mavenCentral()
    }
}
