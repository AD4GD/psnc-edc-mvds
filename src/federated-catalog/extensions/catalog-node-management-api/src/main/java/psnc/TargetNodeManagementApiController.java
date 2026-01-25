package psnc;

import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import org.eclipse.edc.crawler.spi.TargetNodeDirectory;
// import org.eclipse.edc.crawler.spi.TargetNode;  // use actual class
import java.lang.reflect.Method;
import java.util.List;
import org.eclipse.edc.crawler.spi.TargetNode;
import org.eclipse.edc.crawler.spi.TargetNode;
import java.lang.reflect.Constructor;
import java.util.UUID;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

@Consumes(MediaType.APPLICATION_JSON)
@Produces(MediaType.APPLICATION_JSON)
@Path("/v1/targets")
public class TargetNodeManagementApiController {

    private final TargetNodeDirectory directory;

    public TargetNodeManagementApiController(TargetNodeDirectory directory) {
        this.directory = directory;
    }

    @GET
    public Response getAll() {
        // Only supported if the directory exposes a list method
        try {
            Method m = directory.getClass().getMethod("getAll");
            Object result = m.invoke(directory);
            return Response.ok(result).build();
        } catch (NoSuchMethodException e) {
            throw new WebApplicationException(
                    "Listing TargetNodes is not supported by this TargetNodeDirectory implementation",
                    Response.Status.NOT_IMPLEMENTED
            );
        } catch (Exception e) {
            throw new WebApplicationException(e.getMessage(), 500);
        }
    }

    @POST
    public Response create(TargetNodeDto dto) {
        if (dto == null || isBlank(dto.participantId) || isBlank(dto.url)) {
            throw new WebApplicationException("Fields 'participantId' and 'url' are required", 400);
        }

        TargetNode node = new TargetNode(
                dto.participantId,                            
                dto.participantId,                            // participantId = DID
                dto.url,
                dto.supportedProtocols != null ? dto.supportedProtocols : List.of()
        );

        directory.insert(node); // usually acts like upsert in SQL impls
        return Response.status(Response.Status.CREATED).build();
    }

    @DELETE
    @Path("{idB64}")
    public Response delete(@PathParam("idB64") String idB64) {
        if (isBlank(idB64)) {
            throw new WebApplicationException("id is required", 400);
        }

        try {
            String did = decodeDidFromId(idB64);
            directory.remove(did);
            return Response.noContent().build();
        } catch (WebApplicationException e) {
            throw e;
        } catch (Exception e) {
            throw new WebApplicationException("Failed to delete target: " + e.getMessage(), 500);
        }
    }

    private static boolean isBlank(String s) {
        return s == null || s.trim().isEmpty();
    }

    private static String decodeDidFromId(String idB64) {
        try {
            byte[] bytes = Base64.getUrlDecoder().decode(idB64);
            return new String(bytes, StandardCharsets.UTF_8);
        } catch (IllegalArgumentException e) {
            throw new WebApplicationException("Invalid Base64URL id: " + idB64, 400);
    }
}
}
