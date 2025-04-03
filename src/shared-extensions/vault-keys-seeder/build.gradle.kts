
plugins {
    `java-library`
    `maven-publish`
}

dependencies {
    implementation(libs.edc.boot)
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
            artifactId = "vault-keys-seeder"
        }
    }
}
