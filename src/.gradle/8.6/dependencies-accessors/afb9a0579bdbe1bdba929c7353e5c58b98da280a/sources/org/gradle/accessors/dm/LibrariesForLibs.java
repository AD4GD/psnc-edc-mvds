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
 * A catalog of dependencies accessible via the {@code libs} extension.
 */
@NonNullApi
public class LibrariesForLibs extends AbstractExternalDependencyFactory {

    private final AbstractExternalDependencyFactory owner = this;
    private final EdcLibraryAccessors laccForEdcLibraryAccessors = new EdcLibraryAccessors(owner);
    private final FlywayLibraryAccessors laccForFlywayLibraryAccessors = new FlywayLibraryAccessors(owner);
    private final JakartaLibraryAccessors laccForJakartaLibraryAccessors = new JakartaLibraryAccessors(owner);
    private final JettyLibraryAccessors laccForJettyLibraryAccessors = new JettyLibraryAccessors(owner);
    private final SovityLibraryAccessors laccForSovityLibraryAccessors = new SovityLibraryAccessors(owner);
    private final TractusLibraryAccessors laccForTractusLibraryAccessors = new TractusLibraryAccessors(owner);
    private final VersionAccessors vaccForVersionAccessors = new VersionAccessors(providers, config);
    private final BundleAccessors baccForBundleAccessors = new BundleAccessors(objects, providers, config, attributesFactory, capabilityNotationParser);
    private final PluginAccessors paccForPluginAccessors = new PluginAccessors(providers, config);

    @Inject
    public LibrariesForLibs(DefaultVersionCatalog config, ProviderFactory providers, ObjectFactory objects, ImmutableAttributesFactory attributesFactory, CapabilityNotationParser capabilityNotationParser) {
        super(config, providers, objects, attributesFactory, capabilityNotationParser);
    }

    /**
     * Dependency provider for <b>lombok</b> with <b>org.projectlombok:lombok</b> coordinates and
     * with version reference <b>lombok</b>
     * <p>
     * This dependency was declared in catalog libs.versions.toml
     */
    public Provider<MinimalExternalModuleDependency> getLombok() {
        return create("lombok");
    }

    /**
     * Dependency provider for <b>postgresql</b> with <b>org.postgresql:postgresql</b> coordinates and
     * with version reference <b>postgres</b>
     * <p>
     * This dependency was declared in catalog libs.versions.toml
     */
    public Provider<MinimalExternalModuleDependency> getPostgresql() {
        return create("postgresql");
    }

    /**
     * Group of libraries at <b>edc</b>
     */
    public EdcLibraryAccessors getEdc() {
        return laccForEdcLibraryAccessors;
    }

    /**
     * Group of libraries at <b>flyway</b>
     */
    public FlywayLibraryAccessors getFlyway() {
        return laccForFlywayLibraryAccessors;
    }

    /**
     * Group of libraries at <b>jakarta</b>
     */
    public JakartaLibraryAccessors getJakarta() {
        return laccForJakartaLibraryAccessors;
    }

    /**
     * Group of libraries at <b>jetty</b>
     */
    public JettyLibraryAccessors getJetty() {
        return laccForJettyLibraryAccessors;
    }

    /**
     * Group of libraries at <b>sovity</b>
     */
    public SovityLibraryAccessors getSovity() {
        return laccForSovityLibraryAccessors;
    }

    /**
     * Group of libraries at <b>tractus</b>
     */
    public TractusLibraryAccessors getTractus() {
        return laccForTractusLibraryAccessors;
    }

    /**
     * Group of versions at <b>versions</b>
     */
    public VersionAccessors getVersions() {
        return vaccForVersionAccessors;
    }

    /**
     * Group of bundles at <b>bundles</b>
     */
    public BundleAccessors getBundles() {
        return baccForBundleAccessors;
    }

    /**
     * Group of plugins at <b>plugins</b>
     */
    public PluginAccessors getPlugins() {
        return paccForPluginAccessors;
    }

    public static class EdcLibraryAccessors extends SubDependencyFactory {
        private final EdcApiLibraryAccessors laccForEdcApiLibraryAccessors = new EdcApiLibraryAccessors(owner);
        private final EdcAuthLibraryAccessors laccForEdcAuthLibraryAccessors = new EdcAuthLibraryAccessors(owner);
        private final EdcBuildLibraryAccessors laccForEdcBuildLibraryAccessors = new EdcBuildLibraryAccessors(owner);
        private final EdcCallbackLibraryAccessors laccForEdcCallbackLibraryAccessors = new EdcCallbackLibraryAccessors(owner);
        private final EdcConfigurationLibraryAccessors laccForEdcConfigurationLibraryAccessors = new EdcConfigurationLibraryAccessors(owner);
        private final EdcConnectorLibraryAccessors laccForEdcConnectorLibraryAccessors = new EdcConnectorLibraryAccessors(owner);
        private final EdcControlLibraryAccessors laccForEdcControlLibraryAccessors = new EdcControlLibraryAccessors(owner);
        private final EdcCoreLibraryAccessors laccForEdcCoreLibraryAccessors = new EdcCoreLibraryAccessors(owner);
        private final EdcDataLibraryAccessors laccForEdcDataLibraryAccessors = new EdcDataLibraryAccessors(owner);
        private final EdcEdrLibraryAccessors laccForEdcEdrLibraryAccessors = new EdcEdrLibraryAccessors(owner);
        private final EdcFederatedLibraryAccessors laccForEdcFederatedLibraryAccessors = new EdcFederatedLibraryAccessors(owner);
        private final EdcIamLibraryAccessors laccForEdcIamLibraryAccessors = new EdcIamLibraryAccessors(owner);
        private final EdcJsonLibraryAccessors laccForEdcJsonLibraryAccessors = new EdcJsonLibraryAccessors(owner);
        private final EdcManagementLibraryAccessors laccForEdcManagementLibraryAccessors = new EdcManagementLibraryAccessors(owner);
        private final EdcMonitorLibraryAccessors laccForEdcMonitorLibraryAccessors = new EdcMonitorLibraryAccessors(owner);
        private final EdcOauth2LibraryAccessors laccForEdcOauth2LibraryAccessors = new EdcOauth2LibraryAccessors(owner);
        private final EdcSqlLibraryAccessors laccForEdcSqlLibraryAccessors = new EdcSqlLibraryAccessors(owner);
        private final EdcTransactionLibraryAccessors laccForEdcTransactionLibraryAccessors = new EdcTransactionLibraryAccessors(owner);
        private final EdcTransferLibraryAccessors laccForEdcTransferLibraryAccessors = new EdcTransferLibraryAccessors(owner);
        private final EdcValidatorLibraryAccessors laccForEdcValidatorLibraryAccessors = new EdcValidatorLibraryAccessors(owner);
        private final EdcVaultLibraryAccessors laccForEdcVaultLibraryAccessors = new EdcVaultLibraryAccessors(owner);

        public EdcLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>boot</b> with <b>org.eclipse.edc:boot</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getBoot() {
            return create("edc.boot");
        }

        /**
         * Dependency provider for <b>dsp</b> with <b>org.eclipse.edc:dsp</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getDsp() {
            return create("edc.dsp");
        }

        /**
         * Dependency provider for <b>http</b> with <b>org.eclipse.edc:http</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getHttp() {
            return create("edc.http");
        }

        /**
         * Group of libraries at <b>edc.api</b>
         */
        public EdcApiLibraryAccessors getApi() {
            return laccForEdcApiLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.auth</b>
         */
        public EdcAuthLibraryAccessors getAuth() {
            return laccForEdcAuthLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.build</b>
         */
        public EdcBuildLibraryAccessors getBuild() {
            return laccForEdcBuildLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.callback</b>
         */
        public EdcCallbackLibraryAccessors getCallback() {
            return laccForEdcCallbackLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.configuration</b>
         */
        public EdcConfigurationLibraryAccessors getConfiguration() {
            return laccForEdcConfigurationLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.connector</b>
         */
        public EdcConnectorLibraryAccessors getConnector() {
            return laccForEdcConnectorLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.control</b>
         */
        public EdcControlLibraryAccessors getControl() {
            return laccForEdcControlLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.core</b>
         */
        public EdcCoreLibraryAccessors getCore() {
            return laccForEdcCoreLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.data</b>
         */
        public EdcDataLibraryAccessors getData() {
            return laccForEdcDataLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.edr</b>
         */
        public EdcEdrLibraryAccessors getEdr() {
            return laccForEdcEdrLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.federated</b>
         */
        public EdcFederatedLibraryAccessors getFederated() {
            return laccForEdcFederatedLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.iam</b>
         */
        public EdcIamLibraryAccessors getIam() {
            return laccForEdcIamLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.json</b>
         */
        public EdcJsonLibraryAccessors getJson() {
            return laccForEdcJsonLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.management</b>
         */
        public EdcManagementLibraryAccessors getManagement() {
            return laccForEdcManagementLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.monitor</b>
         */
        public EdcMonitorLibraryAccessors getMonitor() {
            return laccForEdcMonitorLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.oauth2</b>
         */
        public EdcOauth2LibraryAccessors getOauth2() {
            return laccForEdcOauth2LibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.sql</b>
         */
        public EdcSqlLibraryAccessors getSql() {
            return laccForEdcSqlLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.transaction</b>
         */
        public EdcTransactionLibraryAccessors getTransaction() {
            return laccForEdcTransactionLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.transfer</b>
         */
        public EdcTransferLibraryAccessors getTransfer() {
            return laccForEdcTransferLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.validator</b>
         */
        public EdcValidatorLibraryAccessors getValidator() {
            return laccForEdcValidatorLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.vault</b>
         */
        public EdcVaultLibraryAccessors getVault() {
            return laccForEdcVaultLibraryAccessors;
        }

    }

    public static class EdcApiLibraryAccessors extends SubDependencyFactory {

        public EdcApiLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>observability</b> with <b>org.eclipse.edc:api-observability</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getObservability() {
            return create("edc.api.observability");
        }

    }

    public static class EdcAuthLibraryAccessors extends SubDependencyFactory {

        public EdcAuthLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>tokenbased</b> with <b>org.eclipse.edc:auth-tokenbased</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getTokenbased() {
            return create("edc.auth.tokenbased");
        }

    }

    public static class EdcBuildLibraryAccessors extends SubDependencyFactory {

        public EdcBuildLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>plugin</b> with <b>org.eclipse.edc.edc-build:org.eclipse.edc.edc-build.gradle.plugin</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getPlugin() {
            return create("edc.build.plugin");
        }

    }

    public static class EdcCallbackLibraryAccessors extends SubDependencyFactory {
        private final EdcCallbackEventLibraryAccessors laccForEdcCallbackEventLibraryAccessors = new EdcCallbackEventLibraryAccessors(owner);
        private final EdcCallbackHttpLibraryAccessors laccForEdcCallbackHttpLibraryAccessors = new EdcCallbackHttpLibraryAccessors(owner);

        public EdcCallbackLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.callback.event</b>
         */
        public EdcCallbackEventLibraryAccessors getEvent() {
            return laccForEdcCallbackEventLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.callback.http</b>
         */
        public EdcCallbackHttpLibraryAccessors getHttp() {
            return laccForEdcCallbackHttpLibraryAccessors;
        }

    }

    public static class EdcCallbackEventLibraryAccessors extends SubDependencyFactory {

        public EdcCallbackEventLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>dispatcher</b> with <b>org.eclipse.edc:callback-event-dispatcher</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getDispatcher() {
            return create("edc.callback.event.dispatcher");
        }

    }

    public static class EdcCallbackHttpLibraryAccessors extends SubDependencyFactory {

        public EdcCallbackHttpLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>dispatcher</b> with <b>org.eclipse.edc:callback-http-dispatcher</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getDispatcher() {
            return create("edc.callback.http.dispatcher");
        }

    }

    public static class EdcConfigurationLibraryAccessors extends SubDependencyFactory {

        public EdcConfigurationLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>filesystem</b> with <b>org.eclipse.edc:configuration-filesystem</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getFilesystem() {
            return create("edc.configuration.filesystem");
        }

    }

    public static class EdcConnectorLibraryAccessors extends SubDependencyFactory {

        public EdcConnectorLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>core</b> with <b>org.eclipse.edc:connector-core</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getCore() {
            return create("edc.connector.core");
        }

    }

    public static class EdcControlLibraryAccessors extends SubDependencyFactory {
        private final EdcControlPlaneLibraryAccessors laccForEdcControlPlaneLibraryAccessors = new EdcControlPlaneLibraryAccessors(owner);

        public EdcControlLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.control.plane</b>
         */
        public EdcControlPlaneLibraryAccessors getPlane() {
            return laccForEdcControlPlaneLibraryAccessors;
        }

    }

    public static class EdcControlPlaneLibraryAccessors extends SubDependencyFactory {
        private final EdcControlPlaneApiLibraryAccessors laccForEdcControlPlaneApiLibraryAccessors = new EdcControlPlaneApiLibraryAccessors(owner);

        public EdcControlPlaneLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>core</b> with <b>org.eclipse.edc:control-plane-core</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getCore() {
            return create("edc.control.plane.core");
        }

        /**
         * Dependency provider for <b>spi</b> with <b>org.eclipse.edc:control-plane-spi</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getSpi() {
            return create("edc.control.plane.spi");
        }

        /**
         * Dependency provider for <b>sql</b> with <b>org.eclipse.edc:control-plane-sql</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getSql() {
            return create("edc.control.plane.sql");
        }

        /**
         * Group of libraries at <b>edc.control.plane.api</b>
         */
        public EdcControlPlaneApiLibraryAccessors getApi() {
            return laccForEdcControlPlaneApiLibraryAccessors;
        }

    }

    public static class EdcControlPlaneApiLibraryAccessors extends SubDependencyFactory implements DependencyNotationSupplier {

        public EdcControlPlaneApiLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>api</b> with <b>org.eclipse.edc:control-plane-api</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> asProvider() {
            return create("edc.control.plane.api");
        }

        /**
         * Dependency provider for <b>client</b> with <b>org.eclipse.edc:control-plane-api-client</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getClient() {
            return create("edc.control.plane.api.client");
        }

    }

    public static class EdcCoreLibraryAccessors extends SubDependencyFactory {

        public EdcCoreLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>spi</b> with <b>org.eclipse.edc:core-spi</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getSpi() {
            return create("edc.core.spi");
        }

    }

    public static class EdcDataLibraryAccessors extends SubDependencyFactory {
        private final EdcDataPlaneLibraryAccessors laccForEdcDataPlaneLibraryAccessors = new EdcDataPlaneLibraryAccessors(owner);

        public EdcDataLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.data.plane</b>
         */
        public EdcDataPlaneLibraryAccessors getPlane() {
            return laccForEdcDataPlaneLibraryAccessors;
        }

    }

    public static class EdcDataPlaneLibraryAccessors extends SubDependencyFactory {
        private final EdcDataPlaneControlLibraryAccessors laccForEdcDataPlaneControlLibraryAccessors = new EdcDataPlaneControlLibraryAccessors(owner);
        private final EdcDataPlaneInstanceLibraryAccessors laccForEdcDataPlaneInstanceLibraryAccessors = new EdcDataPlaneInstanceLibraryAccessors(owner);
        private final EdcDataPlanePublicLibraryAccessors laccForEdcDataPlanePublicLibraryAccessors = new EdcDataPlanePublicLibraryAccessors(owner);
        private final EdcDataPlaneSelectorLibraryAccessors laccForEdcDataPlaneSelectorLibraryAccessors = new EdcDataPlaneSelectorLibraryAccessors(owner);
        private final EdcDataPlaneSelfLibraryAccessors laccForEdcDataPlaneSelfLibraryAccessors = new EdcDataPlaneSelfLibraryAccessors(owner);

        public EdcDataPlaneLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>client</b> with <b>org.eclipse.edc:data-plane-client</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getClient() {
            return create("edc.data.plane.client");
        }

        /**
         * Dependency provider for <b>core</b> with <b>org.eclipse.edc:data-plane-core</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getCore() {
            return create("edc.data.plane.core");
        }

        /**
         * Dependency provider for <b>http</b> with <b>org.eclipse.edc:data-plane-http</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getHttp() {
            return create("edc.data.plane.http");
        }

        /**
         * Dependency provider for <b>spi</b> with <b>org.eclipse.edc:data-plane-spi</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getSpi() {
            return create("edc.data.plane.spi");
        }

        /**
         * Dependency provider for <b>util</b> with <b>org.eclipse.edc:data-plane-util</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getUtil() {
            return create("edc.data.plane.util");
        }

        /**
         * Group of libraries at <b>edc.data.plane.control</b>
         */
        public EdcDataPlaneControlLibraryAccessors getControl() {
            return laccForEdcDataPlaneControlLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.data.plane.instance</b>
         */
        public EdcDataPlaneInstanceLibraryAccessors getInstance() {
            return laccForEdcDataPlaneInstanceLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.data.plane.public</b>
         */
        public EdcDataPlanePublicLibraryAccessors getPublic() {
            return laccForEdcDataPlanePublicLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.data.plane.selector</b>
         */
        public EdcDataPlaneSelectorLibraryAccessors getSelector() {
            return laccForEdcDataPlaneSelectorLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.data.plane.self</b>
         */
        public EdcDataPlaneSelfLibraryAccessors getSelf() {
            return laccForEdcDataPlaneSelfLibraryAccessors;
        }

    }

    public static class EdcDataPlaneControlLibraryAccessors extends SubDependencyFactory {

        public EdcDataPlaneControlLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>api</b> with <b>org.eclipse.edc:data-plane-control-api</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getApi() {
            return create("edc.data.plane.control.api");
        }

    }

    public static class EdcDataPlaneInstanceLibraryAccessors extends SubDependencyFactory {
        private final EdcDataPlaneInstanceStoreLibraryAccessors laccForEdcDataPlaneInstanceStoreLibraryAccessors = new EdcDataPlaneInstanceStoreLibraryAccessors(owner);

        public EdcDataPlaneInstanceLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.data.plane.instance.store</b>
         */
        public EdcDataPlaneInstanceStoreLibraryAccessors getStore() {
            return laccForEdcDataPlaneInstanceStoreLibraryAccessors;
        }

    }

    public static class EdcDataPlaneInstanceStoreLibraryAccessors extends SubDependencyFactory {

        public EdcDataPlaneInstanceStoreLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>sql</b> with <b>org.eclipse.edc:data-plane-instance-store-sql</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getSql() {
            return create("edc.data.plane.instance.store.sql");
        }

    }

    public static class EdcDataPlanePublicLibraryAccessors extends SubDependencyFactory {

        public EdcDataPlanePublicLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>api</b> with <b>org.eclipse.edc:data-plane-public-api-v2</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getApi() {
            return create("edc.data.plane.public.api");
        }

    }

    public static class EdcDataPlaneSelectorLibraryAccessors extends SubDependencyFactory {

        public EdcDataPlaneSelectorLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>api</b> with <b>org.eclipse.edc:data-plane-selector-api</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getApi() {
            return create("edc.data.plane.selector.api");
        }

        /**
         * Dependency provider for <b>client</b> with <b>org.eclipse.edc:data-plane-selector-client</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getClient() {
            return create("edc.data.plane.selector.client");
        }

        /**
         * Dependency provider for <b>core</b> with <b>org.eclipse.edc:data-plane-selector-core</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getCore() {
            return create("edc.data.plane.selector.core");
        }

    }

    public static class EdcDataPlaneSelfLibraryAccessors extends SubDependencyFactory {

        public EdcDataPlaneSelfLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>registration</b> with <b>org.eclipse.edc:data-plane-self-registration</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getRegistration() {
            return create("edc.data.plane.self.registration");
        }

    }

    public static class EdcEdrLibraryAccessors extends SubDependencyFactory {
        private final EdcEdrCacheLibraryAccessors laccForEdcEdrCacheLibraryAccessors = new EdcEdrCacheLibraryAccessors(owner);
        private final EdcEdrStoreLibraryAccessors laccForEdcEdrStoreLibraryAccessors = new EdcEdrStoreLibraryAccessors(owner);

        public EdcEdrLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.edr.cache</b>
         */
        public EdcEdrCacheLibraryAccessors getCache() {
            return laccForEdcEdrCacheLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.edr.store</b>
         */
        public EdcEdrStoreLibraryAccessors getStore() {
            return laccForEdcEdrStoreLibraryAccessors;
        }

    }

    public static class EdcEdrCacheLibraryAccessors extends SubDependencyFactory {

        public EdcEdrCacheLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>api</b> with <b>org.eclipse.edc:edr-cache-api</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getApi() {
            return create("edc.edr.cache.api");
        }

    }

    public static class EdcEdrStoreLibraryAccessors extends SubDependencyFactory {

        public EdcEdrStoreLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>core</b> with <b>org.eclipse.edc:edr-store-core</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getCore() {
            return create("edc.edr.store.core");
        }

        /**
         * Dependency provider for <b>receiver</b> with <b>org.eclipse.edc:edr-store-receiver</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getReceiver() {
            return create("edc.edr.store.receiver");
        }

    }

    public static class EdcFederatedLibraryAccessors extends SubDependencyFactory {
        private final EdcFederatedCatalogLibraryAccessors laccForEdcFederatedCatalogLibraryAccessors = new EdcFederatedCatalogLibraryAccessors(owner);

        public EdcFederatedLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.federated.catalog</b>
         */
        public EdcFederatedCatalogLibraryAccessors getCatalog() {
            return laccForEdcFederatedCatalogLibraryAccessors;
        }

    }

    public static class EdcFederatedCatalogLibraryAccessors extends SubDependencyFactory {

        public EdcFederatedCatalogLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>api</b> with <b>org.eclipse.edc:federated-catalog-api</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getApi() {
            return create("edc.federated.catalog.api");
        }

        /**
         * Dependency provider for <b>core</b> with <b>org.eclipse.edc:federated-catalog-core</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getCore() {
            return create("edc.federated.catalog.core");
        }

    }

    public static class EdcIamLibraryAccessors extends SubDependencyFactory {

        public EdcIamLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>mock</b> with <b>org.eclipse.edc:iam-mock</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getMock() {
            return create("edc.iam.mock");
        }

    }

    public static class EdcJsonLibraryAccessors extends SubDependencyFactory {

        public EdcJsonLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>ld</b> with <b>org.eclipse.edc:json-ld</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getLd() {
            return create("edc.json.ld");
        }

    }

    public static class EdcManagementLibraryAccessors extends SubDependencyFactory {

        public EdcManagementLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>api</b> with <b>org.eclipse.edc:management-api</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getApi() {
            return create("edc.management.api");
        }

    }

    public static class EdcMonitorLibraryAccessors extends SubDependencyFactory {
        private final EdcMonitorJdkLibraryAccessors laccForEdcMonitorJdkLibraryAccessors = new EdcMonitorJdkLibraryAccessors(owner);

        public EdcMonitorLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.monitor.jdk</b>
         */
        public EdcMonitorJdkLibraryAccessors getJdk() {
            return laccForEdcMonitorJdkLibraryAccessors;
        }

    }

    public static class EdcMonitorJdkLibraryAccessors extends SubDependencyFactory {

        public EdcMonitorJdkLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>logger</b> with <b>org.eclipse.edc:monitor-jdk-logger</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getLogger() {
            return create("edc.monitor.jdk.logger");
        }

    }

    public static class EdcOauth2LibraryAccessors extends SubDependencyFactory implements DependencyNotationSupplier {

        public EdcOauth2LibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>oauth2</b> with <b>org.eclipse.edc:oauth2-core</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> asProvider() {
            return create("edc.oauth2");
        }

        /**
         * Dependency provider for <b>core</b> with <b>org.eclipse.edc:oauth2-core</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getCore() {
            return create("edc.oauth2.core");
        }

        /**
         * Dependency provider for <b>daps</b> with <b>org.eclipse.edc:oauth2-daps</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getDaps() {
            return create("edc.oauth2.daps");
        }

    }

    public static class EdcSqlLibraryAccessors extends SubDependencyFactory {
        private final EdcSqlPoolLibraryAccessors laccForEdcSqlPoolLibraryAccessors = new EdcSqlPoolLibraryAccessors(owner);

        public EdcSqlLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>core</b> with <b>org.eclipse.edc:sql-core</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getCore() {
            return create("edc.sql.core");
        }

        /**
         * Group of libraries at <b>edc.sql.pool</b>
         */
        public EdcSqlPoolLibraryAccessors getPool() {
            return laccForEdcSqlPoolLibraryAccessors;
        }

    }

    public static class EdcSqlPoolLibraryAccessors extends SubDependencyFactory {
        private final EdcSqlPoolApacheLibraryAccessors laccForEdcSqlPoolApacheLibraryAccessors = new EdcSqlPoolApacheLibraryAccessors(owner);

        public EdcSqlPoolLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.sql.pool.apache</b>
         */
        public EdcSqlPoolApacheLibraryAccessors getApache() {
            return laccForEdcSqlPoolApacheLibraryAccessors;
        }

    }

    public static class EdcSqlPoolApacheLibraryAccessors extends SubDependencyFactory {

        public EdcSqlPoolApacheLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>commons</b> with <b>org.eclipse.edc:sql-pool-apache-commons</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getCommons() {
            return create("edc.sql.pool.apache.commons");
        }

    }

    public static class EdcTransactionLibraryAccessors extends SubDependencyFactory {

        public EdcTransactionLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>local</b> with <b>org.eclipse.edc:transaction-local</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getLocal() {
            return create("edc.transaction.local");
        }

    }

    public static class EdcTransferLibraryAccessors extends SubDependencyFactory {
        private final EdcTransferDataLibraryAccessors laccForEdcTransferDataLibraryAccessors = new EdcTransferDataLibraryAccessors(owner);
        private final EdcTransferPullLibraryAccessors laccForEdcTransferPullLibraryAccessors = new EdcTransferPullLibraryAccessors(owner);

        public EdcTransferLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>spi</b> with <b>org.eclipse.edc:transfer-spi</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getSpi() {
            return create("edc.transfer.spi");
        }

        /**
         * Group of libraries at <b>edc.transfer.data</b>
         */
        public EdcTransferDataLibraryAccessors getData() {
            return laccForEdcTransferDataLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.transfer.pull</b>
         */
        public EdcTransferPullLibraryAccessors getPull() {
            return laccForEdcTransferPullLibraryAccessors;
        }

    }

    public static class EdcTransferDataLibraryAccessors extends SubDependencyFactory {
        private final EdcTransferDataPlaneLibraryAccessors laccForEdcTransferDataPlaneLibraryAccessors = new EdcTransferDataPlaneLibraryAccessors(owner);

        public EdcTransferDataLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.transfer.data.plane</b>
         */
        public EdcTransferDataPlaneLibraryAccessors getPlane() {
            return laccForEdcTransferDataPlaneLibraryAccessors;
        }

    }

    public static class EdcTransferDataPlaneLibraryAccessors extends SubDependencyFactory implements DependencyNotationSupplier {

        public EdcTransferDataPlaneLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>plane</b> with <b>org.eclipse.edc:transfer-data-plane</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> asProvider() {
            return create("edc.transfer.data.plane");
        }

        /**
         * Dependency provider for <b>signaling</b> with <b>org.eclipse.edc:transfer-data-plane-signaling</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getSignaling() {
            return create("edc.transfer.data.plane.signaling");
        }

    }

    public static class EdcTransferPullLibraryAccessors extends SubDependencyFactory {
        private final EdcTransferPullHttpLibraryAccessors laccForEdcTransferPullHttpLibraryAccessors = new EdcTransferPullHttpLibraryAccessors(owner);

        public EdcTransferPullLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.transfer.pull.http</b>
         */
        public EdcTransferPullHttpLibraryAccessors getHttp() {
            return laccForEdcTransferPullHttpLibraryAccessors;
        }

    }

    public static class EdcTransferPullHttpLibraryAccessors extends SubDependencyFactory {

        public EdcTransferPullHttpLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>receiver</b> with <b>org.eclipse.edc:transfer-pull-http-receiver</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getReceiver() {
            return create("edc.transfer.pull.http.receiver");
        }

    }

    public static class EdcValidatorLibraryAccessors extends SubDependencyFactory {
        private final EdcValidatorDataLibraryAccessors laccForEdcValidatorDataLibraryAccessors = new EdcValidatorDataLibraryAccessors(owner);

        public EdcValidatorLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.validator.data</b>
         */
        public EdcValidatorDataLibraryAccessors getData() {
            return laccForEdcValidatorDataLibraryAccessors;
        }

    }

    public static class EdcValidatorDataLibraryAccessors extends SubDependencyFactory {
        private final EdcValidatorDataAddressLibraryAccessors laccForEdcValidatorDataAddressLibraryAccessors = new EdcValidatorDataAddressLibraryAccessors(owner);

        public EdcValidatorDataLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.validator.data.address</b>
         */
        public EdcValidatorDataAddressLibraryAccessors getAddress() {
            return laccForEdcValidatorDataAddressLibraryAccessors;
        }

    }

    public static class EdcValidatorDataAddressLibraryAccessors extends SubDependencyFactory {
        private final EdcValidatorDataAddressHttpLibraryAccessors laccForEdcValidatorDataAddressHttpLibraryAccessors = new EdcValidatorDataAddressHttpLibraryAccessors(owner);

        public EdcValidatorDataAddressLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.validator.data.address.http</b>
         */
        public EdcValidatorDataAddressHttpLibraryAccessors getHttp() {
            return laccForEdcValidatorDataAddressHttpLibraryAccessors;
        }

    }

    public static class EdcValidatorDataAddressHttpLibraryAccessors extends SubDependencyFactory {

        public EdcValidatorDataAddressHttpLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>data</b> with <b>org.eclipse.edc:validator-data-address-http-data</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getData() {
            return create("edc.validator.data.address.http.data");
        }

    }

    public static class EdcVaultLibraryAccessors extends SubDependencyFactory {

        public EdcVaultLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>filesystem</b> with <b>org.eclipse.edc:vault-filesystem</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getFilesystem() {
            return create("edc.vault.filesystem");
        }

    }

    public static class FlywayLibraryAccessors extends SubDependencyFactory {

        public FlywayLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>core</b> with <b>org.flywaydb:flyway-core</b> coordinates and
         * with version reference <b>flyway</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getCore() {
            return create("flyway.core");
        }

    }

    public static class JakartaLibraryAccessors extends SubDependencyFactory {

        public JakartaLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>rsApi</b> with <b>jakarta.ws.rs:jakarta.ws.rs-api</b> coordinates and
         * with version reference <b>rsApi</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getRsApi() {
            return create("jakarta.rsApi");
        }

    }

    public static class JettyLibraryAccessors extends SubDependencyFactory {
        private final JettyJakartaLibraryAccessors laccForJettyJakartaLibraryAccessors = new JettyJakartaLibraryAccessors(owner);

        public JettyLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>jetty.jakarta</b>
         */
        public JettyJakartaLibraryAccessors getJakarta() {
            return laccForJettyJakartaLibraryAccessors;
        }

    }

    public static class JettyJakartaLibraryAccessors extends SubDependencyFactory {
        private final JettyJakartaServletLibraryAccessors laccForJettyJakartaServletLibraryAccessors = new JettyJakartaServletLibraryAccessors(owner);

        public JettyJakartaLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>jetty.jakarta.servlet</b>
         */
        public JettyJakartaServletLibraryAccessors getServlet() {
            return laccForJettyJakartaServletLibraryAccessors;
        }

    }

    public static class JettyJakartaServletLibraryAccessors extends SubDependencyFactory {

        public JettyJakartaServletLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>api</b> with <b>org.eclipse.jetty.toolchain:jetty-jakarta-servlet-api</b> coordinates and
         * with version reference <b>jetty.jakarta.servlet.api</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getApi() {
            return create("jetty.jakarta.servlet.api");
        }

    }

    public static class SovityLibraryAccessors extends SubDependencyFactory {

        public SovityLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>pgflyway</b> with <b>de.sovity.edc.ext:postgres-flyway</b> coordinates and
         * with version reference <b>sovityext</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getPgflyway() {
            return create("sovity.pgflyway");
        }

    }

    public static class TractusLibraryAccessors extends SubDependencyFactory {
        private final TractusPostgresqlLibraryAccessors laccForTractusPostgresqlLibraryAccessors = new TractusPostgresqlLibraryAccessors(owner);

        public TractusLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>tractus.postgresql</b>
         */
        public TractusPostgresqlLibraryAccessors getPostgresql() {
            return laccForTractusPostgresqlLibraryAccessors;
        }

    }

    public static class TractusPostgresqlLibraryAccessors extends SubDependencyFactory {
        private final TractusPostgresqlControlLibraryAccessors laccForTractusPostgresqlControlLibraryAccessors = new TractusPostgresqlControlLibraryAccessors(owner);
        private final TractusPostgresqlDataLibraryAccessors laccForTractusPostgresqlDataLibraryAccessors = new TractusPostgresqlDataLibraryAccessors(owner);

        public TractusPostgresqlLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>tractus.postgresql.control</b>
         */
        public TractusPostgresqlControlLibraryAccessors getControl() {
            return laccForTractusPostgresqlControlLibraryAccessors;
        }

        /**
         * Group of libraries at <b>tractus.postgresql.data</b>
         */
        public TractusPostgresqlDataLibraryAccessors getData() {
            return laccForTractusPostgresqlDataLibraryAccessors;
        }

    }

    public static class TractusPostgresqlControlLibraryAccessors extends SubDependencyFactory {
        private final TractusPostgresqlControlPlaneLibraryAccessors laccForTractusPostgresqlControlPlaneLibraryAccessors = new TractusPostgresqlControlPlaneLibraryAccessors(owner);

        public TractusPostgresqlControlLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>tractus.postgresql.control.plane</b>
         */
        public TractusPostgresqlControlPlaneLibraryAccessors getPlane() {
            return laccForTractusPostgresqlControlPlaneLibraryAccessors;
        }

    }

    public static class TractusPostgresqlControlPlaneLibraryAccessors extends SubDependencyFactory {

        public TractusPostgresqlControlPlaneLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>migration</b> with <b>org.eclipse.tractusx.edc:control-plane-migration</b> coordinates and
         * with version reference <b>tractus</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getMigration() {
            return create("tractus.postgresql.control.plane.migration");
        }

    }

    public static class TractusPostgresqlDataLibraryAccessors extends SubDependencyFactory {
        private final TractusPostgresqlDataPlaneLibraryAccessors laccForTractusPostgresqlDataPlaneLibraryAccessors = new TractusPostgresqlDataPlaneLibraryAccessors(owner);

        public TractusPostgresqlDataLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>tractus.postgresql.data.plane</b>
         */
        public TractusPostgresqlDataPlaneLibraryAccessors getPlane() {
            return laccForTractusPostgresqlDataPlaneLibraryAccessors;
        }

    }

    public static class TractusPostgresqlDataPlaneLibraryAccessors extends SubDependencyFactory {

        public TractusPostgresqlDataPlaneLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>migration</b> with <b>org.eclipse.tractusx.edc:data-plane-migration</b> coordinates and
         * with version reference <b>tractus</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getMigration() {
            return create("tractus.postgresql.data.plane.migration");
        }

    }

    public static class VersionAccessors extends VersionFactory  {

        private final JakartaVersionAccessors vaccForJakartaVersionAccessors = new JakartaVersionAccessors(providers, config);
        private final JettyVersionAccessors vaccForJettyVersionAccessors = new JettyVersionAccessors(providers, config);
        private final JunitVersionAccessors vaccForJunitVersionAccessors = new JunitVersionAccessors(providers, config);
        private final OkhttpVersionAccessors vaccForOkhttpVersionAccessors = new OkhttpVersionAccessors(providers, config);
        public VersionAccessors(ProviderFactory providers, DefaultVersionCatalog config) { super(providers, config); }

        /**
         * Version alias <b>assertj</b> with value <b>3.24.2</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getAssertj() { return getVersion("assertj"); }

        /**
         * Version alias <b>awaitility</b> with value <b>4.2.0</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getAwaitility() { return getVersion("awaitility"); }

        /**
         * Version alias <b>edc</b> with value <b>0.7.0</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getEdc() { return getVersion("edc"); }

        /**
         * Version alias <b>flyway</b> with value <b>9.0.1</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getFlyway() { return getVersion("flyway"); }

        /**
         * Version alias <b>jupiter</b> with value <b>5.10.0</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getJupiter() { return getVersion("jupiter"); }

        /**
         * Version alias <b>kafkaClients</b> with value <b>3.6.0</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getKafkaClients() { return getVersion("kafkaClients"); }

        /**
         * Version alias <b>lombok</b> with value <b>1.18.28</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getLombok() { return getVersion("lombok"); }

        /**
         * Version alias <b>openTelemetry</b> with value <b>1.18.0</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getOpenTelemetry() { return getVersion("openTelemetry"); }

        /**
         * Version alias <b>postgres</b> with value <b>42.4.0</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getPostgres() { return getVersion("postgres"); }

        /**
         * Version alias <b>restAssured</b> with value <b>5.3.2</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getRestAssured() { return getVersion("restAssured"); }

        /**
         * Version alias <b>rsApi</b> with value <b>3.1.0</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getRsApi() { return getVersion("rsApi"); }

        /**
         * Version alias <b>sovityext</b> with value <b>4.2.0</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getSovityext() { return getVersion("sovityext"); }

        /**
         * Version alias <b>testcontainers</b> with value <b>1.19.1</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getTestcontainers() { return getVersion("testcontainers"); }

        /**
         * Version alias <b>tractus</b> with value <b>0.7.2</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getTractus() { return getVersion("tractus"); }

        /**
         * Group of versions at <b>versions.jakarta</b>
         */
        public JakartaVersionAccessors getJakarta() {
            return vaccForJakartaVersionAccessors;
        }

        /**
         * Group of versions at <b>versions.jetty</b>
         */
        public JettyVersionAccessors getJetty() {
            return vaccForJettyVersionAccessors;
        }

        /**
         * Group of versions at <b>versions.junit</b>
         */
        public JunitVersionAccessors getJunit() {
            return vaccForJunitVersionAccessors;
        }

        /**
         * Group of versions at <b>versions.okhttp</b>
         */
        public OkhttpVersionAccessors getOkhttp() {
            return vaccForOkhttpVersionAccessors;
        }

    }

    public static class JakartaVersionAccessors extends VersionFactory  {

        public JakartaVersionAccessors(ProviderFactory providers, DefaultVersionCatalog config) { super(providers, config); }

        /**
         * Version alias <b>jakarta.json</b> with value <b>2.0.1</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getJson() { return getVersion("jakarta.json"); }

    }

    public static class JettyVersionAccessors extends VersionFactory  {

        private final JettyJakartaVersionAccessors vaccForJettyJakartaVersionAccessors = new JettyJakartaVersionAccessors(providers, config);
        public JettyVersionAccessors(ProviderFactory providers, DefaultVersionCatalog config) { super(providers, config); }

        /**
         * Group of versions at <b>versions.jetty.jakarta</b>
         */
        public JettyJakartaVersionAccessors getJakarta() {
            return vaccForJettyJakartaVersionAccessors;
        }

    }

    public static class JettyJakartaVersionAccessors extends VersionFactory  {

        private final JettyJakartaServletVersionAccessors vaccForJettyJakartaServletVersionAccessors = new JettyJakartaServletVersionAccessors(providers, config);
        public JettyJakartaVersionAccessors(ProviderFactory providers, DefaultVersionCatalog config) { super(providers, config); }

        /**
         * Group of versions at <b>versions.jetty.jakarta.servlet</b>
         */
        public JettyJakartaServletVersionAccessors getServlet() {
            return vaccForJettyJakartaServletVersionAccessors;
        }

    }

    public static class JettyJakartaServletVersionAccessors extends VersionFactory  {

        public JettyJakartaServletVersionAccessors(ProviderFactory providers, DefaultVersionCatalog config) { super(providers, config); }

        /**
         * Version alias <b>jetty.jakarta.servlet.api</b> with value <b>5.0.2</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getApi() { return getVersion("jetty.jakarta.servlet.api"); }

    }

    public static class JunitVersionAccessors extends VersionFactory  {

        public JunitVersionAccessors(ProviderFactory providers, DefaultVersionCatalog config) { super(providers, config); }

        /**
         * Version alias <b>junit.pioneer</b> with value <b>2.1.0</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getPioneer() { return getVersion("junit.pioneer"); }

    }

    public static class OkhttpVersionAccessors extends VersionFactory  {

        public OkhttpVersionAccessors(ProviderFactory providers, DefaultVersionCatalog config) { super(providers, config); }

        /**
         * Version alias <b>okhttp.mockwebserver</b> with value <b>5.0.0-alpha.11</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
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
         * Plugin provider for <b>shadow</b> with plugin id <b>com.github.johnrengelman.shadow</b> and
         * with version <b>8.1.1</b>
         * <p>
         * This plugin was declared in catalog libs.versions.toml
         */
        public Provider<PluginDependency> getShadow() { return createPlugin("shadow"); }

    }

}
