// not used anymore, they move to the lib.versions.toml. Remove after testing.
val edcVersion: String by project
val edcGroup: String by project
val flywayVersion: String by project
val postgresVersion: String by project


plugins {
    `java-library`
}

dependencies {

    annotationProcessor(libs.lombok)
    compileOnly(libs.lombok)
    
    implementation(libs.edc.core.spi) //implementation("${edcGroup}:core-spi:${edcVersion}")
    implementation(libs.edc.sql.core) //implementation("${edcGroup}:sql-core:${edcVersion}")

    // Adds Database-Related EDC-Extensions (EDC-SQL-Stores, JDBC-Driver, Pool and Transactions)
    implementation(libs.edc.control.plane.sql) //implementation("${edcGroup}:control-plane-sql:${edcVersion}")
    implementation(libs.edc.data.plane.instance.store.sql) //implementation("${edcGroup}:data-plane-instance-store-sql:${edcVersion}")
    implementation(libs.edc.sql.pool.apache.commons) //implementation("${edcGroup}:sql-pool-apache-commons:${edcVersion}")
    implementation(libs.edc.transaction.local) //implementation("${edcGroup}:transaction-local:${edcVersion}")

    implementation(libs.postgresql) //implementation("org.postgresql:postgresql:${postgresVersion}")

    implementation(libs.flyway.core) //implementation("org.flywaydb:flyway-core:${flywayVersion}")
}

