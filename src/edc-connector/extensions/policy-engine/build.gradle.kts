
plugins {
    `java-library`
}

dependencies {
    implementation(libs.edc.contract.spi)
    implementation(libs.edc.policy.engine.spi)
    implementation(libs.edc.participant.spi)
    implementation(libs.edc.jsonld.spi)
    implementation(libs.edc.connector.core)
}
