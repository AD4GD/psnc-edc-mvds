
plugins {
    `java-library`
    `maven-publish`
}

dependencies {
    implementation(libs.edc.boot)
    api(libs.edc.auth.spi)
    implementation(libs.jakarta.rsApi)

    implementation(libs.edc.auth.configuration)
    implementation(libs.edc.auth.tokenbased)
    implementation(libs.edc.auth.delegated)
    implementation(libs.edc.core.token)
}

group = "com.psnc.mvds"
version = "1.0.0"

publishing {
    repositories {
        mavenLocal()
    }
    publications {
        create<MavenPublication>("mavenJava") {
            from(components["java"])
            artifactId = "auth-composite"
        }
    }
}
