
plugins {
    `java-library`
}

dependencies {
    implementation(libs.edc.boot)
    api(libs.edc.auth.spi)
    implementation(libs.jakarta.rsApi)
}