/*
*  Copyright (c) 2023 Bayerische Motoren Werke Aktiengesellschaft (BMW AG)
*
*  This program and the accompanying materials are made available under the
*  terms of the Apache License, Version 2.0 which is available at
*  https://www.apache.org/licenses/LICENSE-2.0
*
*  SPDX-License-Identifier: Apache-2.0
*
*  Contributors:
*       Bayerische Motoren Werke Aktiengesellschaft (BMW AG) - Initial API and Implementation
*
*/

plugins {
    `java-library`
    id("application")
    alias(libs.plugins.shadow)
}

dependencies {
    // control plane part
    runtimeOnly(project(":extensions:did-example-resolver"))
    runtimeOnly(project(":extensions:dcp-impl")) // some patches/impls for DCP
    runtimeOnly(libs.edc.bom.controlplane)
    runtimeOnly(libs.edc.api.secrets)
    runtimeOnly(project(":extensions:data-plane-oauth2-access-token"))
    runtimeOnly(project(":extensions:policy-engine"))

    // data plane part
    runtimeOnly(libs.edc.bom.dataplane)
    runtimeOnly(libs.edc.dataplane.v2)

    implementation(libs.edc.configuration.filesystem)

    implementation(libs.psnc.auth.composite)

    if (project.properties.getOrDefault("persistence", "false") == "true") {
        runtimeOnly(libs.bundles.edc.sql.control.plane)
        runtimeOnly(libs.bundles.edc.sql.data.plane)
    }
}

tasks.withType<com.github.jengelman.gradle.plugins.shadow.tasks.ShadowJar> {
    exclude("**/pom.properties", "**/pom.xml")
    mergeServiceFiles()
    archiveFileName.set("connector.jar")
}

application {
    mainClass.set("org.eclipse.edc.boot.system.runtime.BaseRuntime")
}

edcBuild {
    publish.set(false)
}
