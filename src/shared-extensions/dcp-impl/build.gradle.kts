
plugins {
    `java-library`
    `maven-publish`
}

dependencies {
    implementation(libs.edc.dcp.core)
    implementation(libs.edc.spi.identity.trust)
    implementation(libs.edc.spi.transform)
    implementation(libs.edc.spi.catalog)
    implementation(libs.edc.spi.identity.did)
    implementation(libs.edc.lib.jws2020)
    implementation(libs.edc.lib.transform)
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
            artifactId = "dcp-impl"
        }
    }
}
