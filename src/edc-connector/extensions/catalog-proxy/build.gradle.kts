
plugins {
    `java-library`
}

dependencies {
    implementation(libs.edc.core.spi)
    implementation(libs.edc.control.plane.spi)
    implementation(libs.edc.catalog.spi)
    implementation(libs.edc.web.spi)
    implementation(libs.jakarta.rsApi)

    // Using SPIs usually sufficient.
    // If I need to send CatalogRequest, it might be in control-plane-spi or catalog-spi
}
