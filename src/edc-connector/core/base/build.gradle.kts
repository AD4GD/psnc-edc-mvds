
plugins {
    `java-library`
}

dependencies {
    implementation(libs.edc.control.plane.api.client)
    implementation(libs.edc.control.plane.api)
    implementation(libs.edc.control.plane.core)
    implementation(libs.edc.dsp)
    implementation(libs.edc.configuration.filesystem)
    implementation(libs.edc.management.api)
    implementation(libs.edc.http)

    implementation(libs.edc.transfer.data.plane.signaling)

    // required for consumer PULL transfer type
    implementation(libs.edc.data.plane.iam)
    implementation(libs.edc.token.core)

    implementation(libs.edc.control.api.configuration)

    implementation(libs.edc.transfer.pull.http.receiver)
    implementation(libs.edc.validator.data.address.http.data)

    implementation(libs.edc.edr.cache.api)
    implementation(libs.edc.edr.store.core)
    implementation(libs.edc.edr.store.receiver)

    implementation(libs.edc.data.plane.selector.api)
    implementation(libs.edc.data.plane.selector.core)

    implementation(libs.edc.data.plane.self.registration)

    implementation(libs.edc.data.plane.signaling.api)

    implementation(libs.edc.data.plane.public.api)
    implementation(libs.edc.data.plane.core)
    implementation(libs.edc.data.plane.http)
    implementation(project(":extensions:data-plane-oauth2-access-token"))

    implementation(libs.edc.api.observability)

    implementation(libs.psnc.auth.composite)

    // enable callbacks
    implementation(libs.edc.callback.event.dispatcher)
    implementation(libs.edc.callback.http.dispatcher)

    implementation(project(":extensions:policy-engine"))
}
