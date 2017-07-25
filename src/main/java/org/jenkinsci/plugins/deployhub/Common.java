package org.jenkinsci.plugins.deployhub;

// For calls to the API
import java.io.BufferedReader;
import java.io.File;
import java.io.FilenameFilter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.List;

import javax.xml.parsers.DocumentBuilder;
// for XML parsing
import javax.xml.parsers.DocumentBuilderFactory;

import org.kohsuke.stapler.StaplerRequest;
import org.kohsuke.stapler.StaplerResponse;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

import hudson.XmlFile;
import hudson.model.Action;
import hudson.model.Hudson;
import jenkins.model.Jenkins;
import jenkins.model.ModelObjectWithContextMenu;

public abstract class Common implements Action, ModelObjectWithContextMenu {

    public String getDisplayName() {
	return getClass().getSimpleName();
    }

    public String getUrlName() {
	return getClass().getSimpleName();
    }

    public List<DeployHubMenu> getAll() {
        return null;
    }

    public String getViewUrl() {
	return "deployhub";
    }

    public ContextMenu doContextMenu(StaplerRequest request, StaplerResponse response) throws Exception {
        return new ContextMenu().addAll(getAll());
    }

    public static String getServerURL()
    {
    Jenkins jenkins = Jenkins.getInstance();
    if (jenkins == null)
     return "";
    
	String rootDir = jenkins.getRootDir().getAbsolutePath();
        XmlFile t = new XmlFile(Hudson.XSTREAM, new File(rootDir, "org.jenkinsci.plugins.deployhub.DeployHub.xml"));
        if (t != null && t.exists()) {
                try {   
                        DeployHubRecorder.DescriptorImpl desc = (DeployHubRecorder.DescriptorImpl)t.read();
                        if (desc != null) return desc.getServerURL();
                        return "";
                } catch(IOException ex) {
                }
        }
        return "";
    }

    public HashMap<String,String> getUserAccounts()
    {
	HashMap<String,String> res = new HashMap<String,String>();
    Jenkins jenkins = Jenkins.getInstance();
    if (jenkins == null)
      return res;
    
	String baseurl = getServerURL();

	String rootDir = jenkins.getRootDir().getAbsolutePath();
	String jobsDir = rootDir + "/jobs";
	// Get list of job folders
	File file = new File(jobsDir);
	
	String[] directories = new String[0];
	
	if (file != null)
	{
	 directories = file.list(new FilenameFilter() {
		@Override
		public boolean accept(File current, String name) {
			return new File(current, name).isDirectory();
		}
	 });
	}
	
	for (int i=0;i<directories.length;i++) {
		try {
			DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
			DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
			File configFile = new File(jobsDir+"/"+directories[i], "config.xml");
			if (!configFile.exists()) continue;
			Document doc = dBuilder.parse(configFile);
			doc.getDocumentElement().normalize();
			Element baseNode = doc.getDocumentElement();
			NodeList publishers = baseNode.getElementsByTagName("publishers");
			if (publishers != null && publishers.getLength()>0) {
				Element p = (Element)(publishers.item(0));
				NodeList dhElements = p.getElementsByTagName("org.jenkinsci.plugins.deployhub.DeployHub");
				if (dhElements != null && dhElements.getLength()>0) {
					// Found our plugin as a post-build (publisher) step.
					Element n = (Element)(dhElements.item(0));
					Element username = (Element)(n.getElementsByTagName("username").item(0));
					Element password = (Element)(n.getElementsByTagName("password").item(0));
					if (username != null && password != null) {
						System.out.println("username="+username.getTextContent());	
						System.out.println("password="+password.getTextContent());
						String url=baseurl+"/dmadminweb/API/XXXuser="+username.getTextContent()+"&pass="+password.getTextContent();
						res.put(url,directories[i]);
					}
				}
			}
		} catch(Exception ex) {
			System.out.println("Exception ex = "+ex.getMessage());
		}
	}
	return res;
    }

    public String httpGet(String url) throws Exception {
	URL obj = new URL(url);
	HttpURLConnection con = (HttpURLConnection) obj.openConnection();

	con.setRequestMethod("GET");
	con.setRequestProperty("User-Agent","Mozilla/5.0");
	con.getResponseCode();
	BufferedReader in = new BufferedReader(new InputStreamReader(con.getInputStream(),StandardCharsets.UTF_8));
	String inputLine;
	StringBuffer response = new StringBuffer();

	while ((inputLine = in.readLine()) != null) {
		response.append(inputLine);
	}
	in.close();
	return response.toString();
    }
}
