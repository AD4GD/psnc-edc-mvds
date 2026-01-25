package psnc;

import java.util.List;

public class TargetNodeDto {
    /** Participant identifier / node identifier you want to crawl (e.g., DID) */
    public String participantId;

    /** Target DSP (or catalog) base URL */
    public String url;

    /** Optional supported protocols */
    public List<String> supportedProtocols;
}
