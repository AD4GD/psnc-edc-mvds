plugins {
    `java-library`
}

dependencies {
    api(libs.edc.token.spi)
    api(libs.edc.jwt.spi)
    api(libs.edc.oauth2.spi)
    api(libs.edc.data.plane.spi)
    api(libs.edc.data.plane.http)
}
