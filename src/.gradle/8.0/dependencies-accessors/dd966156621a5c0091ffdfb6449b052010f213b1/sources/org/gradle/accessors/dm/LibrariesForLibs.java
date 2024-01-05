package org.gradle.accessors.dm;

import org.gradle.api.NonNullApi;
import org.gradle.api.artifacts.MinimalExternalModuleDependency;
import org.gradle.plugin.use.PluginDependency;
import org.gradle.api.artifacts.ExternalModuleDependencyBundle;
import org.gradle.api.artifacts.MutableVersionConstraint;
import org.gradle.api.provider.Provider;
import org.gradle.api.model.ObjectFactory;
import org.gradle.api.provider.ProviderFactory;
import org.gradle.api.internal.catalog.AbstractExternalDependencyFactory;
import org.gradle.api.internal.catalog.DefaultVersionCatalog;
import java.util.Map;
import org.gradle.api.internal.attributes.ImmutableAttributesFactory;
import org.gradle.api.internal.artifacts.dsl.CapabilityNotationParser;
import javax.inject.Inject;

/**
 * A catalog of dependencies accessible via the `libs` extension.
*/
@NonNullApi
public class LibrariesForLibs extends AbstractExternalDependencyFactory {

    private final AbstractExternalDependencyFactory owner = this;
    private final EdcLibraryAccessors laccForEdcLibraryAccessors = new EdcLibraryAccessors(owner);
    private final FlywayLibraryAccessors laccForFlywayLibraryAccessors = new FlywayLibraryAccessors(owner);
    private final JakartaLibraryAccessors laccForJakartaLibraryAccessors = new JakartaLibraryAccessors(owner);
    private final JettyLibraryAccessors laccForJettyLibraryAccessors = new JettyLibraryAccessors(owner);
    private final SovityLibraryAccessors laccForSovityLibraryAccessors = new SovityLibraryAccessors(owner);
    private final VersionAccessors vaccForVersionAccessors = new VersionAccessors(providers, config);
    private final BundleAccessors baccForBundleAccessors = new BundleAccessors(objects, providers, config, attributesFactory, capabilityNotationParser);
    private final PluginAccessors paccForPluginAccessors = new PluginAccessors(providers, config);

    @Inject
    public LibrariesForLibs(DefaultVersionCatalog config, ProviderFactory providers, ObjectFactory objects, ImmutableAttributesFactory attributesFactory, CapabilityNotationParser capabilityNotationParser) {
        super(config, providers, objects, attributesFactory, capabilityNotationParser);
    }

        /**
         * Creates a dependency provider for lombok (org.projectlombok:lombok)
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getLombok() { return create("lombok"); }

        /**
         * Creates a dependency provider for postgresql (org.postgresql:postgresql)
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getPostgresql() { return create("postgresql"); }

    /**
     * Returns the group of libraries at edc
     */
    public EdcLibraryAccessors getEdc() { return laccForEdcLibraryAccessors; }

    /**
     * Returns the group of libraries at flyway
     */
    public FlywayLibraryAccessors getFlyway() { return laccForFlywayLibraryAccessors; }

    /**
     * Returns the group of libraries at jakarta
     */
    public JakartaLibraryAccessors getJakarta() { return laccForJakartaLibraryAccessors; }

    /**
     * Returns the group of libraries at jetty
     */
    public JettyLibraryAccessors getJetty() { return laccForJettyLibraryAccessors; }

    /**
     * Returns the group of libraries at sovity
     */
    public SovityLibraryAccessors getSovity() { return laccForSovityLibraryAccessors; }

    /**
     * Returns the group of versions at versions
     */
    public VersionAccessors getVersions() { return vaccForVersionAccessors; }

    /**
     * Returns the group of bundles at bundles
     */
    public BundleAccessors getBundles() { return baccForBundleAccessors; }

    /**
     * Returns the group of plugins at plugins
     */
    public PluginAccessors getPlugins() { return paccForPluginAccessors; }

    public static class EdcLibraryAccessors extends SubDependencyFactory {
        private final EdcApiLibraryAccessors laccForEdcApiLibraryAccessors = new EdcApiLibraryAccessors(owner);
        private final EdcAuthLibraryAccessors laccForEdcAuthLibraryAccessors = new EdcAuthLibraryAccessors(owner);
        private final EdcBuildLibraryAccessors laccForEdcBuildLibraryAccessors = new EdcBuildLibraryAccessors(owner);
        private final EdcConfigurationLibraryAccessors laccForEdcConfigurationLibraryAccessors = new EdcConfigurationLibraryAccessors(owner);
        private final EdcConnectorLibraryAccessors laccForEdcConnectorLibraryAccessors = new EdcConnectorLibraryAccessors(owner);
        private final EdcControlLibraryAccessors laccForEdcControlLibraryAccessors = new EdcControlLibraryAccessors(owner);
        private final EdcCoreLibraryAccessors laccForEdcCoreLibraryAccessors = new EdcCoreLibraryAccessors(owner);
        private final EdcDataLibraryAccessors laccForEdcDataLibraryAccessors = new EdcDataLibraryAccessors(owner);
        private final EdcFederatedLibraryAccessors laccForEdcFederatedLibraryAccessors = new EdcFederatedLibraryAccessors(owner);
        private final EdcIamLibraryAccessors laccForEdcIamLibraryAccessors = new EdcIamLibraryAccessors(owner);
        private final EdcJsonLibraryAccessors laccForEdcJsonLibraryAccessors = new EdcJsonLibraryAccessors(owner);
        private final EdcManagementLibraryAccessors laccForEdcManagementLibraryAccessors = new EdcManagementLibraryAccessors(owner);
        private final EdcMonitorLibraryAccessors laccForEdcMonitorLibraryAccessors = new EdcMonitorLibraryAccessors(owner);
        private final EdcSqlLibraryAccessors laccForEdcSqlLibraryAccessors = new EdcSqlLibraryAccessors(owner);
        private final EdcTransactionLibraryAccessors laccForEdcTransactionLibraryAccessors = new EdcTransactionLibraryAccessors(owner);
        private final EdcTransferLibraryAccessors laccForEdcTransferLibraryAccessors = new EdcTransferLibraryAccessors(owner);
        private final EdcVaultLibraryAccessors laccForEdcVaultLibraryAccessors = new EdcVaultLibraryAccessors(owner);

        public EdcLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

            /**
             * Creates a dependency provider for boot (org.eclipse.edc:boot)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getBoot() { return create("edc.boot"); }

            /**
             * Creates a dependency provider for dsp (org.eclipse.edc:dsp)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getDsp() { return create("edc.dsp"); }

            /**
             * Creates a dependency provider for http (org.eclipse.edc:http)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getHttp() { return create("edc.http"); }

            /**
             * Creates a dependency provider for oauth2 (org.eclipse.edc:oauth2-core)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getOauth2() { return create("edc.oauth2"); }

        /**
         * Returns the group of libraries at edc.api
         */
        public EdcApiLibraryAccessors getApi() { return laccForEdcApiLibraryAccessors; }

        /**
         * Returns the group of libraries at edc.auth
         */
        public EdcAuthLibraryAccessors getAuth() { return laccForEdcAuthLibraryAccessors; }

        /**
         * Returns the group of libraries at edc.build
         */
        public EdcBuildLibraryAccessors getBuild() { return laccForEdcBuildLibraryAccessors; }

        /**
         * Returns the group of libraries at edc.configuration
         */
        public EdcConfigurationLibraryAccessors getConfiguration() { return laccForEdcConfigurationLibraryAccessors; }

        /**
         * Returns the group of libraries at edc.connector
         */
        public EdcConnectorLibraryAccessors getConnector() { return laccForEdcConnectorLibraryAccessors; }

        /**
         * Returns the group of libraries at edc.control
         */
        public EdcControlLibraryAccessors getControl() { return laccForEdcControlLibraryAccessors; }

        /**
         * Returns the group of libraries at edc.core
         */
        public EdcCoreLibraryAccessors getCore() { return laccForEdcCoreLibraryAccessors; }

        /**
         * Returns the group of libraries at edc.data
         */
        public EdcDataLibraryAccessors getData() { return laccForEdcDataLibraryAccessors; }

        /**
         * Returns the group of libraries at edc.federated
         */
        public EdcFederatedLibraryAccessors getFederated() { return laccForEdcFederatedLibraryAccessors; }

        /**
         * Returns the group of libraries at edc.iam
         */
        public EdcIamLibraryAccessors getIam() { return laccForEdcIamLibraryAccessors; }

        /**
         * Returns the group of libraries at edc.json
         */
        public EdcJsonLibraryAccessors getJson() { return laccForEdcJsonLibraryAccessors; }

        /**
         * Returns the group of libraries at edc.management
         */
        public EdcManagementLibraryAccessors getManagement() { return laccForEdcManagementLibraryAccessors; }

        /**
         * Returns the group of libraries at edc.monitor
         */
        public EdcMonitorLibraryAccessors getMonitor() { return laccForEdcMonitorLibraryAccessors; }

        /**
         * Returns the group of libraries at edc.sql
         */
        public EdcSqlLibraryAccessors getSql() { return laccForEdcSqlLibraryAccessors; }

        /**
         * Returns the group of libraries at edc.transaction
         */
        public EdcTransactionLibraryAccessors getTransaction() { return laccForEdcTransactionLibraryAccessors; }

        /**
         * Returns the group of libraries at edc.transfer
         */
        public EdcTransferLibraryAccessors getTransfer() { return laccForEdcTransferLibraryAccessors; }

        /**
         * Returns the group of libraries at edc.vault
         */
        public EdcVaultLibraryAccessors getVault() { return laccForEdcVaultLibraryAccessors; }

    }

    public static class EdcApiLibraryAccessors extends SubDependencyFactory {

        public EdcApiLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

            /**
             * Creates a dependency provider for observability (org.eclipse.edc:api-observability)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getObservability() { return create("edc.api.observability"); }

    }

    public static class EdcAuthLibraryAccessors extends SubDependencyFactory {

        public EdcAuthLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

            /**
             * Creates a dependency provider for tokenbased (org.eclipse.edc:auth-tokenbased)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getTokenbased() { return create("edc.auth.tokenbased"); }

    }

    public static class EdcBuildLibraryAccessors extends SubDependencyFactory {

        public EdcBuildLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

            /**
             * Creates a dependency provider for plugin (org.eclipse.edc.edc-build:org.eclipse.edc.edc-build.gradle.plugin)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getPlugin() { return create("edc.build.plugin"); }

    }

    public static class EdcConfigurationLibraryAccessors extends SubDependencyFactory {

        public EdcConfigurationLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

            /**
             * Creates a dependency provider for filesystem (org.eclipse.edc:configuration-filesystem)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getFilesystem() { return create("edc.configuration.filesystem"); }

    }

    public static class EdcConnectorLibraryAccessors extends SubDependencyFactory {

        public EdcConnectorLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

            /**
             * Creates a dependency provider for core (org.eclipse.edc:connector-core)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getCore() { return create("edc.connector.core"); }

    }

    public static class EdcControlLibraryAccessors extends SubDependencyFactory {
        private final EdcControlPlaneLibraryAccessors laccForEdcControlPlaneLibraryAccessors = new EdcControlPlaneLibraryAccessors(owner);

        public EdcControlLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Returns the group of libraries at edc.control.plane
         */
        public EdcControlPlaneLibraryAccessors getPlane() { return laccForEdcControlPlaneLibraryAccessors; }

    }

    public static class EdcControlPlaneLibraryAccessors extends SubDependencyFactory {
        private final EdcControlPlaneApiLibraryAccessors laccForEdcControlPlaneApiLibraryAccessors = new EdcControlPlaneApiLibraryAccessors(owner);

        public EdcControlPlaneLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

            /**
             * Creates a dependency provider for core (org.eclipse.edc:control-plane-core)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getCore() { return create("edc.control.plane.core"); }

            /**
             * Creates a dependency provider for spi (org.eclipse.edc:control-plane-spi)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getSpi() { return create("edc.control.plane.spi"); }

            /**
             * Creates a dependency provider for sql (org.eclipse.edc:control-plane-sql)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getSql() { return create("edc.control.plane.sql"); }

        /**
         * Returns the group of libraries at edc.control.plane.api
         */
        public EdcControlPlaneApiLibraryAccessors getApi() { return laccForEdcControlPlaneApiLibraryAccessors; }

    }

    public static class EdcControlPlaneApiLibraryAccessors extends SubDependencyFactory implements DependencyNotationSupplier {

        public EdcControlPlaneApiLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

            /**
             * Creates a dependency provider for api (org.eclipse.edc:control-plane-api)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> asProvider() { return create("edc.control.plane.api"); }

            /**
             * Creates a dependency provider for client (org.eclipse.edc:control-plane-api-client)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getClient() { return create("edc.control.plane.api.client"); }

    }

    public static class EdcCoreLibraryAccessors extends SubDependencyFactory {

        public EdcCoreLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

            /**
             * Creates a dependency provider for spi (org.eclipse.edc:core-spi)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getSpi() { return create("edc.core.spi"); }

    }

    public static class EdcDataLibraryAccessors extends SubDependencyFactory {
        private final EdcDataPlaneLibraryAccessors laccForEdcDataPlaneLibraryAccessors = new EdcDataPlaneLibraryAccessors(owner);

        public EdcDataLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Returns the group of libraries at edc.data.plane
         */
        public EdcDataPlaneLibraryAccessors getPlane() { return laccForEdcDataPlaneLibraryAccessors; }

    }

    public static class EdcDataPlaneLibraryAccessors extends SubDependencyFactory {
        private final EdcDataPlaneInstanceLibraryAccessors laccForEdcDataPlaneInstanceLibraryAccessors = new EdcDataPlaneInstanceLibraryAccessors(owner);
        private final EdcDataPlaneSelectorLibraryAccessors laccForEdcDataPlaneSelectorLibraryAccessors = new EdcDataPlaneSelectorLibraryAccessors(owner);

        public EdcDataPlaneLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

            /**
             * Creates a dependency provider for api (org.eclipse.edc:data-plane-api)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getApi() { return create("edc.data.plane.api"); }

            /**
             * Creates a dependency provider for client (org.eclipse.edc:data-plane-client)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getClient() { return create("edc.data.plane.client"); }

            /**
             * Creates a dependency provider for core (org.eclipse.edc:data-plane-core)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getCore() { return create("edc.data.plane.core"); }

            /**
             * Creates a dependency provider for http (org.eclipse.edc:data-plane-http)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getHttp() { return create("edc.data.plane.http"); }

            /**
             * Creates a dependency provider for spi (org.eclipse.edc:data-plane-spi)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getSpi() { return create("edc.data.plane.spi"); }

            /**
             * Creates a dependency provider for util (org.eclipse.edc:data-plane-util)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getUtil() { return create("edc.data.plane.util"); }

        /**
         * Returns the group of libraries at edc.data.plane.instance
         */
        public EdcDataPlaneInstanceLibraryAccessors getInstance() { return laccForEdcDataPlaneInstanceLibraryAccessors; }

        /**
         * Returns the group of libraries at edc.data.plane.selector
         */
        public EdcDataPlaneSelectorLibraryAccessors getSelector() { return laccForEdcDataPlaneSelectorLibraryAccessors; }

    }

    public static class EdcDataPlaneInstanceLibraryAccessors extends SubDependencyFactory {
        private final EdcDataPlaneInstanceStoreLibraryAccessors laccForEdcDataPlaneInstanceStoreLibraryAccessors = new EdcDataPlaneInstanceStoreLibraryAccessors(owner);

        public EdcDataPlaneInstanceLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Returns the group of libraries at edc.data.plane.instance.store
         */
        public EdcDataPlaneInstanceStoreLibraryAccessors getStore() { return laccForEdcDataPlaneInstanceStoreLibraryAccessors; }

    }

    public static class EdcDataPlaneInstanceStoreLibraryAccessors extends SubDependencyFactory {

        public EdcDataPlaneInstanceStoreLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

            /**
             * Creates a dependency provider for sql (org.eclipse.edc:data-plane-instance-store-sql)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getSql() { return create("edc.data.plane.instance.store.sql"); }

    }

    public static class EdcDataPlaneSelectorLibraryAccessors extends SubDependencyFactory {

        public EdcDataPlaneSelectorLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

            /**
             * Creates a dependency provider for api (org.eclipse.edc:data-plane-selector-api)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getApi() { return create("edc.data.plane.selector.api"); }

            /**
             * Creates a dependency provider for client (org.eclipse.edc:data-plane-selector-client)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getClient() { return create("edc.data.plane.selector.client"); }

            /**
             * Creates a dependency provider for core (org.eclipse.edc:data-plane-selector-core)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getCore() { return create("edc.data.plane.selector.core"); }

    }

    public static class EdcFederatedLibraryAccessors extends SubDependencyFactory {
        private final EdcFederatedCatalogLibraryAccessors laccForEdcFederatedCatalogLibraryAccessors = new EdcFederatedCatalogLibraryAccessors(owner);

        public EdcFederatedLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Returns the group of libraries at edc.federated.catalog
         */
        public EdcFederatedCatalogLibraryAccessors getCatalog() { return laccForEdcFederatedCatalogLibraryAccessors; }

    }

    public static class EdcFederatedCatalogLibraryAccessors extends SubDependencyFactory {

        public EdcFederatedCatalogLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

            /**
             * Creates a dependency provider for api (org.eclipse.edc:federated-catalog-api)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getApi() { return create("edc.federated.catalog.api"); }

            /**
             * Creates a dependency provider for core (org.eclipse.edc:federated-catalog-core)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getCore() { return create("edc.federated.catalog.core"); }

    }

    public static class EdcIamLibraryAccessors extends SubDependencyFactory {

        public EdcIamLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

            /**
             * Creates a dependency provider for mock (org.eclipse.edc:iam-mock)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getMock() { return create("edc.iam.mock"); }

    }

    public static class EdcJsonLibraryAccessors extends SubDependencyFactory {

        public EdcJsonLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

            /**
             * Creates a dependency provider for ld (org.eclipse.edc:json-ld)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getLd() { return create("edc.json.ld"); }

    }

    public static class EdcManagementLibraryAccessors extends SubDependencyFactory {

        public EdcManagementLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

            /**
             * Creates a dependency provider for api (org.eclipse.edc:management-api)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getApi() { return create("edc.management.api"); }

    }

    public static class EdcMonitorLibraryAccessors extends SubDependencyFactory {
        private final EdcMonitorJdkLibraryAccessors laccForEdcMonitorJdkLibraryAccessors = new EdcMonitorJdkLibraryAccessors(owner);

        public EdcMonitorLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Returns the group of libraries at edc.monitor.jdk
         */
        public EdcMonitorJdkLibraryAccessors getJdk() { return laccForEdcMonitorJdkLibraryAccessors; }

    }

    public static class EdcMonitorJdkLibraryAccessors extends SubDependencyFactory {

        public EdcMonitorJdkLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

            /**
             * Creates a dependency provider for logger (org.eclipse.edc:monitor-jdk-logger)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getLogger() { return create("edc.monitor.jdk.logger"); }

    }

    public static class EdcSqlLibraryAccessors extends SubDependencyFactory {
        private final EdcSqlPoolLibraryAccessors laccForEdcSqlPoolLibraryAccessors = new EdcSqlPoolLibraryAccessors(owner);

        public EdcSqlLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

            /**
             * Creates a dependency provider for core (org.eclipse.edc:sql-core)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getCore() { return create("edc.sql.core"); }

        /**
         * Returns the group of libraries at edc.sql.pool
         */
        public EdcSqlPoolLibraryAccessors getPool() { return laccForEdcSqlPoolLibraryAccessors; }

    }

    public static class EdcSqlPoolLibraryAccessors extends SubDependencyFactory {
        private final EdcSqlPoolApacheLibraryAccessors laccForEdcSqlPoolApacheLibraryAccessors = new EdcSqlPoolApacheLibraryAccessors(owner);

        public EdcSqlPoolLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Returns the group of libraries at edc.sql.pool.apache
         */
        public EdcSqlPoolApacheLibraryAccessors getApache() { return laccForEdcSqlPoolApacheLibraryAccessors; }

    }

    public static class EdcSqlPoolApacheLibraryAccessors extends SubDependencyFactory {

        public EdcSqlPoolApacheLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

            /**
             * Creates a dependency provider for commons (org.eclipse.edc:sql-pool-apache-commons)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getCommons() { return create("edc.sql.pool.apache.commons"); }

    }

    public static class EdcTransactionLibraryAccessors extends SubDependencyFactory {

        public EdcTransactionLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

            /**
             * Creates a dependency provider for local (org.eclipse.edc:transaction-local)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getLocal() { return create("edc.transaction.local"); }

    }

    public static class EdcTransferLibraryAccessors extends SubDependencyFactory {
        private final EdcTransferDataLibraryAccessors laccForEdcTransferDataLibraryAccessors = new EdcTransferDataLibraryAccessors(owner);
        private final EdcTransferPullLibraryAccessors laccForEdcTransferPullLibraryAccessors = new EdcTransferPullLibraryAccessors(owner);

        public EdcTransferLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

            /**
             * Creates a dependency provider for spi (org.eclipse.edc:transfer-spi)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getSpi() { return create("edc.transfer.spi"); }

        /**
         * Returns the group of libraries at edc.transfer.data
         */
        public EdcTransferDataLibraryAccessors getData() { return laccForEdcTransferDataLibraryAccessors; }

        /**
         * Returns the group of libraries at edc.transfer.pull
         */
        public EdcTransferPullLibraryAccessors getPull() { return laccForEdcTransferPullLibraryAccessors; }

    }

    public static class EdcTransferDataLibraryAccessors extends SubDependencyFactory {

        public EdcTransferDataLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

            /**
             * Creates a dependency provider for plane (org.eclipse.edc:transfer-data-plane)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getPlane() { return create("edc.transfer.data.plane"); }

    }

    public static class EdcTransferPullLibraryAccessors extends SubDependencyFactory {
        private final EdcTransferPullHttpLibraryAccessors laccForEdcTransferPullHttpLibraryAccessors = new EdcTransferPullHttpLibraryAccessors(owner);

        public EdcTransferPullLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Returns the group of libraries at edc.transfer.pull.http
         */
        public EdcTransferPullHttpLibraryAccessors getHttp() { return laccForEdcTransferPullHttpLibraryAccessors; }

    }

    public static class EdcTransferPullHttpLibraryAccessors extends SubDependencyFactory {

        public EdcTransferPullHttpLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

            /**
             * Creates a dependency provider for receiver (org.eclipse.edc:transfer-pull-http-receiver)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getReceiver() { return create("edc.transfer.pull.http.receiver"); }

    }

    public static class EdcVaultLibraryAccessors extends SubDependencyFactory {

        public EdcVaultLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

            /**
             * Creates a dependency provider for filesystem (org.eclipse.edc:vault-filesystem)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getFilesystem() { return create("edc.vault.filesystem"); }

    }

    public static class FlywayLibraryAccessors extends SubDependencyFactory {

        public FlywayLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

            /**
             * Creates a dependency provider for core (org.flywaydb:flyway-core)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getCore() { return create("flyway.core"); }

    }

    public static class JakartaLibraryAccessors extends SubDependencyFactory {

        public JakartaLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

            /**
             * Creates a dependency provider for rsApi (jakarta.ws.rs:jakarta.ws.rs-api)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getRsApi() { return create("jakarta.rsApi"); }

    }

    public static class JettyLibraryAccessors extends SubDependencyFactory {
        private final JettyJakartaLibraryAccessors laccForJettyJakartaLibraryAccessors = new JettyJakartaLibraryAccessors(owner);

        public JettyLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Returns the group of libraries at jetty.jakarta
         */
        public JettyJakartaLibraryAccessors getJakarta() { return laccForJettyJakartaLibraryAccessors; }

    }

    public static class JettyJakartaLibraryAccessors extends SubDependencyFactory {
        private final JettyJakartaServletLibraryAccessors laccForJettyJakartaServletLibraryAccessors = new JettyJakartaServletLibraryAccessors(owner);

        public JettyJakartaLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Returns the group of libraries at jetty.jakarta.servlet
         */
        public JettyJakartaServletLibraryAccessors getServlet() { return laccForJettyJakartaServletLibraryAccessors; }

    }

    public static class JettyJakartaServletLibraryAccessors extends SubDependencyFactory {

        public JettyJakartaServletLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

            /**
             * Creates a dependency provider for api (org.eclipse.jetty.toolchain:jetty-jakarta-servlet-api)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getApi() { return create("jetty.jakarta.servlet.api"); }

    }

    public static class SovityLibraryAccessors extends SubDependencyFactory {

        public SovityLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

            /**
             * Creates a dependency provider for pgflyway (de.sovity.edc.ext:postgres-flyway)
             * This dependency was declared in catalog libs.versions.toml
             */
            public Provider<MinimalExternalModuleDependency> getPgflyway() { return create("sovity.pgflyway"); }

    }

    public static class VersionAccessors extends VersionFactory  {

        private final JakartaVersionAccessors vaccForJakartaVersionAccessors = new JakartaVersionAccessors(providers, config);
        private final JettyVersionAccessors vaccForJettyVersionAccessors = new JettyVersionAccessors(providers, config);
        private final JunitVersionAccessors vaccForJunitVersionAccessors = new JunitVersionAccessors(providers, config);
        private final OkhttpVersionAccessors vaccForOkhttpVersionAccessors = new OkhttpVersionAccessors(providers, config);
        public VersionAccessors(ProviderFactory providers, DefaultVersionCatalog config) { super(providers, config); }

            /**
             * Returns the version associated to this alias: assertj (3.24.2)
             * If the version is a rich version and that its not expressible as a
             * single version string, then an empty string is returned.
             * This version was declared in catalog libs.versions.toml
             */
            public Provider<String> getAssertj() { return getVersion("assertj"); }

            /**
             * Returns the version associated to this alias: awaitility (4.2.0)
             * If the version is a rich version and that its not expressible as a
             * single version string, then an empty string is returned.
             * This version was declared in catalog libs.versions.toml
             */
            public Provider<String> getAwaitility() { return getVersion("awaitility"); }

            /**
             * Returns the version associated to this alias: edc (0.3.1)
             * If the version is a rich version and that its not expressible as a
             * single version string, then an empty string is returned.
             * This version was declared in catalog libs.versions.toml
             */
            public Provider<String> getEdc() { return getVersion("edc"); }

            /**
             * Returns the version associated to this alias: flyway (9.0.1)
             * If the version is a rich version and that its not expressible as a
             * single version string, then an empty string is returned.
             * This version was declared in catalog libs.versions.toml
             */
            public Provider<String> getFlyway() { return getVersion("flyway"); }

            /**
             * Returns the version associated to this alias: jupiter (5.10.0)
             * If the version is a rich version and that its not expressible as a
             * single version string, then an empty string is returned.
             * This version was declared in catalog libs.versions.toml
             */
            public Provider<String> getJupiter() { return getVersion("jupiter"); }

            /**
             * Returns the version associated to this alias: kafkaClients (3.6.0)
             * If the version is a rich version and that its not expressible as a
             * single version string, then an empty string is returned.
             * This version was declared in catalog libs.versions.toml
             */
            public Provider<String> getKafkaClients() { return getVersion("kafkaClients"); }

            /**
             * Returns the version associated to this alias: lombok (1.18.28)
             * If the version is a rich version and that its not expressible as a
             * single version string, then an empty string is returned.
             * This version was declared in catalog libs.versions.toml
             */
            public Provider<String> getLombok() { return getVersion("lombok"); }

            /**
             * Returns the version associated to this alias: openTelemetry (1.18.0)
             * If the version is a rich version and that its not expressible as a
             * single version string, then an empty string is returned.
             * This version was declared in catalog libs.versions.toml
             */
            public Provider<String> getOpenTelemetry() { return getVersion("openTelemetry"); }

            /**
             * Returns the version associated to this alias: postgres (42.4.0)
             * If the version is a rich version and that its not expressible as a
             * single version string, then an empty string is returned.
             * This version was declared in catalog libs.versions.toml
             */
            public Provider<String> getPostgres() { return getVersion("postgres"); }

            /**
             * Returns the version associated to this alias: restAssured (5.3.2)
             * If the version is a rich version and that its not expressible as a
             * single version string, then an empty string is returned.
             * This version was declared in catalog libs.versions.toml
             */
            public Provider<String> getRestAssured() { return getVersion("restAssured"); }

            /**
             * Returns the version associated to this alias: rsApi (3.1.0)
             * If the version is a rich version and that its not expressible as a
             * single version string, then an empty string is returned.
             * This version was declared in catalog libs.versions.toml
             */
            public Provider<String> getRsApi() { return getVersion("rsApi"); }

            /**
             * Returns the version associated to this alias: sovityext (4.2.0)
             * If the version is a rich version and that its not expressible as a
             * single version string, then an empty string is returned.
             * This version was declared in catalog libs.versions.toml
             */
            public Provider<String> getSovityext() { return getVersion("sovityext"); }

            /**
             * Returns the version associated to this alias: testcontainers (1.19.1)
             * If the version is a rich version and that its not expressible as a
             * single version string, then an empty string is returned.
             * This version was declared in catalog libs.versions.toml
             */
            public Provider<String> getTestcontainers() { return getVersion("testcontainers"); }

        /**
         * Returns the group of versions at versions.jakarta
         */
        public JakartaVersionAccessors getJakarta() { return vaccForJakartaVersionAccessors; }

        /**
         * Returns the group of versions at versions.jetty
         */
        public JettyVersionAccessors getJetty() { return vaccForJettyVersionAccessors; }

        /**
         * Returns the group of versions at versions.junit
         */
        public JunitVersionAccessors getJunit() { return vaccForJunitVersionAccessors; }

        /**
         * Returns the group of versions at versions.okhttp
         */
        public OkhttpVersionAccessors getOkhttp() { return vaccForOkhttpVersionAccessors; }

    }

    public static class JakartaVersionAccessors extends VersionFactory  {

        public JakartaVersionAccessors(ProviderFactory providers, DefaultVersionCatalog config) { super(providers, config); }

            /**
             * Returns the version associated to this alias: jakarta.json (2.0.1)
             * If the version is a rich version and that its not expressible as a
             * single version string, then an empty string is returned.
             * This version was declared in catalog libs.versions.toml
             */
            public Provider<String> getJson() { return getVersion("jakarta.json"); }

    }

    public static class JettyVersionAccessors extends VersionFactory  {

        private final JettyJakartaVersionAccessors vaccForJettyJakartaVersionAccessors = new JettyJakartaVersionAccessors(providers, config);
        public JettyVersionAccessors(ProviderFactory providers, DefaultVersionCatalog config) { super(providers, config); }

        /**
         * Returns the group of versions at versions.jetty.jakarta
         */
        public JettyJakartaVersionAccessors getJakarta() { return vaccForJettyJakartaVersionAccessors; }

    }

    public static class JettyJakartaVersionAccessors extends VersionFactory  {

        private final JettyJakartaServletVersionAccessors vaccForJettyJakartaServletVersionAccessors = new JettyJakartaServletVersionAccessors(providers, config);
        public JettyJakartaVersionAccessors(ProviderFactory providers, DefaultVersionCatalog config) { super(providers, config); }

        /**
         * Returns the group of versions at versions.jetty.jakarta.servlet
         */
        public JettyJakartaServletVersionAccessors getServlet() { return vaccForJettyJakartaServletVersionAccessors; }

    }

    public static class JettyJakartaServletVersionAccessors extends VersionFactory  {

        public JettyJakartaServletVersionAccessors(ProviderFactory providers, DefaultVersionCatalog config) { super(providers, config); }

            /**
             * Returns the version associated to this alias: jetty.jakarta.servlet.api (5.0.2)
             * If the version is a rich version and that its not expressible as a
             * single version string, then an empty string is returned.
             * This version was declared in catalog libs.versions.toml
             */
            public Provider<String> getApi() { return getVersion("jetty.jakarta.servlet.api"); }

    }

    public static class JunitVersionAccessors extends VersionFactory  {

        public JunitVersionAccessors(ProviderFactory providers, DefaultVersionCatalog config) { super(providers, config); }

            /**
             * Returns the version associated to this alias: junit.pioneer (2.1.0)
             * If the version is a rich version and that its not expressible as a
             * single version string, then an empty string is returned.
             * This version was declared in catalog libs.versions.toml
             */
            public Provider<String> getPioneer() { return getVersion("junit.pioneer"); }

    }

    public static class OkhttpVersionAccessors extends VersionFactory  {

        public OkhttpVersionAccessors(ProviderFactory providers, DefaultVersionCatalog config) { super(providers, config); }

            /**
             * Returns the version associated to this alias: okhttp.mockwebserver (5.0.0-alpha.11)
             * If the version is a rich version and that its not expressible as a
             * single version string, then an empty string is returned.
             * This version was declared in catalog libs.versions.toml
             */
            public Provider<String> getMockwebserver() { return getVersion("okhttp.mockwebserver"); }

    }

    public static class BundleAccessors extends BundleFactory {

        public BundleAccessors(ObjectFactory objects, ProviderFactory providers, DefaultVersionCatalog config, ImmutableAttributesFactory attributesFactory, CapabilityNotationParser capabilityNotationParser) { super(objects, providers, config, attributesFactory, capabilityNotationParser); }

    }

    public static class PluginAccessors extends PluginFactory {

        public PluginAccessors(ProviderFactory providers, DefaultVersionCatalog config) { super(providers, config); }

            /**
             * Creates a plugin provider for shadow to the plugin id 'com.github.johnrengelman.shadow'
             * This plugin was declared in catalog libs.versions.toml
             */
            public Provider<PluginDependency> getShadow() { return createPlugin("shadow"); }

    }

}
