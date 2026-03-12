
plugins {
    `java-library`
    `maven-publish`
}

dependencies {
    implementation(libs.edc.boot)
    api(libs.edc.spi)
    implementation(libs.jakarta.rsApi)
    implementation(libs.edc.http)
    implementation(libs.edc.jwt.spi)
    implementation(libs.nimbus.jose.jwt)
    implementation(libs.jackson.databind)
    
    // OkHttp client
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    
    // OpenAPI annotations for API documentation
    implementation("io.swagger.core.v3:swagger-annotations-jakarta:2.2.20")
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
            artifactId = "ishare-participant-registry"
        }
    }
}
