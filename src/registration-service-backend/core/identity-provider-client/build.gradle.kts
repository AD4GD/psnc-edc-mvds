plugins {
    `java-library`
}

dependencies {
    implementation(libs.edc.spi.core)
    implementation(libs.edc.core.api)
    implementation(libs.edc.ext.http)
    //implementation(libs.edc.ext.identity.did.crypto)
    implementation(libs.keycloak.admin.client)
}

