
plugins {
    `java-library`
}

dependencies {
    implementation(libs.edc.spi.core)
    implementation(libs.edc.spi.control.plane)
    implementation(libs.edc.spi.catalog)
    implementation(libs.edc.spi.web)
    implementation(libs.jakarta.rsApi)

    // Using SPIs usually sufficient.
    // If I need to send CatalogRequest, it might be in control-plane-spi or catalog-spi
}
