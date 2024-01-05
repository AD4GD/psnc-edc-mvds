/*
 *  Copyright (c) 2021 Microsoft Corporation
 *
 *  This program and the accompanying materials are made available under the
 *  terms of the Apache License, Version 2.0 which is available at
 *  https://www.apache.org/licenses/LICENSE-2.0
 *
 *  SPDX-License-Identifier: Apache-2.0
 *
 *  Contributors:
 *       Microsoft Corporation - Initial implementation
 *
 */

package org.eclipse.edc.extension.assetcollect;

import org.eclipse.edc.spi.EdcException;
import org.eclipse.edc.spi.monitor.Monitor;

import java.io.FileReader;
import java.io.StringReader;

import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.URL;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Stream;
import java.util.stream.Collectors;

import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

import jakarta.json.Json;
import jakarta.json.JsonObject;
import jakarta.json.JsonString;

import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.InputSource;

@Consumes({MediaType.APPLICATION_JSON})
@Produces({MediaType.APPLICATION_JSON})
@Path("/")
public class ApiCollector {
    private Monitor monitor;
    private String filename, web_management_path, web_management_port;

    public ApiCollector(Monitor monitor,
                        String filename,
                        String web_management_path,
                        String web_management_port) {
        this.monitor = monitor;
        this.filename = filename;
        this.web_management_path = web_management_path;
        this.web_management_port = web_management_port;
    }

    public static JsonObject readJsonFromFile(String filename) throws Exception {
        var jsonReader = Json.createReader(new FileReader(filename));
        return jsonReader.readObject();
    }

    public URL getApiCollectRequestUrl(JsonObject apiCollection) throws Exception{
        Set<String> paramsSet = new HashSet<>();

        JsonObject paramsObject = apiCollection.getJsonObject("params");
        if (paramsObject == null){
            return null;
        }

        paramsObject.forEach((key, value) -> {
            String fieldName = key;
            String fieldValue = ((JsonString) value).getString();
            paramsSet.add(fieldName + "=" + fieldValue);
        });

        String urlString = apiCollection.getString("url") + "?" + String.join("&", paramsSet);
        return new URL(urlString);

    }

    public Stream<String> getResponseFromApi(JsonObject apiCollection) throws Exception {
        var url = getApiCollectRequestUrl(apiCollection);
        var method = apiCollection.getString("method");

        var httpClient = HttpClient.newHttpClient();
        var httpRequest = HttpRequest.newBuilder()
                .uri(new URL(url.toString()).toURI())
                .method(method, HttpRequest.BodyPublishers.noBody())
                .build();

        HttpResponse<String> response = httpClient.send(httpRequest, HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() != 200) {
            throw new Exception("API request failed with status code: " + response.statusCode());
        }

        String responseBody = response.body();
        return Arrays.stream(responseBody.split("\\r?\\n"));
    }

    public NodeList parseXml(Stream<String> stringStream, String parentTag) throws Exception {
        var xmlString = stringStream.collect(Collectors.joining());

        var dbFactory = DocumentBuilderFactory.newInstance();
        var dBuilder = dbFactory.newDocumentBuilder();
        var doc = dBuilder.parse(new InputSource(new StringReader(xmlString)));

        return doc.getElementsByTagName(parentTag);
    }

    public String substituteFeatureValues(String assetDraft, Set<String> features_keys, Node xobjNode) {
        String outputDraft = assetDraft;
        if(xobjNode.hasChildNodes()) {
            NodeList childNodes = xobjNode.getChildNodes();
            for(int j = 0; j < childNodes.getLength(); j++) {
                Node childNode = childNodes.item(j);

                for(var key : features_keys){
                    if(key.equals(childNode.getNodeName())) {
                        outputDraft = outputDraft.replace("<"+key+">", childNode.getTextContent());
                    }
                }
            }
        }
        return outputDraft;
    }

    public void getAssetsFromOutput(Stream<String> output, JsonObject apiCollection) throws Exception {
        var outputMapping = apiCollection.getJsonObject("output_mapping");
        var parentTag = outputMapping.getString("pattern");
        var format = outputMapping.getString("format");

        var assetScheme = apiCollection.getJsonObject("asset_scheme");
        var features_keys = findWordsInChevrons(assetScheme.toString());

        var xobjNodes = parseXml(output, parentTag);

        for(var r : features_keys){
            monitor.info(r);
        }

        for(int i = 0; i < xobjNodes.getLength(); i++) {
            Node xobjNode = xobjNodes.item(i);
            var ac = substituteFeatureValues(assetScheme.toString(), features_keys, xobjNode);
        }
    }

    public static Set<String> findWordsInChevrons(String input) {
        Set<String> wordsInCurlyBrackets = new HashSet<>();
        Pattern pattern = Pattern.compile("<([^>]+?)>");
        Matcher matcher = pattern.matcher(input);
        while (matcher.find()) {
            String match = matcher.group(1); // Get the word inside curly brackets
            wordsInCurlyBrackets.add(match);
        }
        return wordsInCurlyBrackets;
    }

    public void createAsset(String assetData) throws Exception {
        var url = new URL("http://localhost:" + this.web_management_port + "/" + this.web_management_path + "/v3/assets");

        var client = HttpClient.newHttpClient();
        var request = HttpRequest.newBuilder(url.toURI())
                .header("Content-Type", "application/json")
                .header("Accept", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(assetData, StandardCharsets.UTF_8))
                .build();

        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

        monitor.info("Automatic asset creation finished, response code: " + response.statusCode());

        if(response.statusCode() != 200){
            monitor.info(response.body());
        }
    }

    @GET
    @Path("apicollect")
    public String collectAssets() {
        try{
            var filepath = Paths.get(filename);

            if (!Files.exists(filepath)) {
                throw new EdcException("Asset collection file does not exist: " + filename);
            }
            monitor.info("Received an Api Collect request " + filename);
            JsonObject ACW = readJsonFromFile(filename);

            var keyset = ACW.keySet();

            for(var iterator = ACW.keySet().iterator(); iterator.hasNext();) {
                String key = (String) iterator.next();
                var apiCollection = (JsonObject) ACW.get(key);
                var responseStream = getResponseFromApi(apiCollection);
                getAssetsFromOutput(responseStream, apiCollection);
            }
        }
        catch(Exception e){
            e.printStackTrace();
        }
        return "{\"response\":\" We've got it \"}";
    }
}
