package org.jenkinsci.plugins.deployhub;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

import org.kohsuke.stapler.bind.JavaScriptMethod;

import hudson.Extension;
import hudson.model.Action;

@Extension
public class Applications extends Common {
    public String getIconFileName() {
        return "/plugin/deployhub/images/application.png";
    }

    public Action getDynamic(String name) {
	System.out.println("Applications - getDynamic("+name+")");
	return new Application(name);
    }

@JavaScriptMethod
    public String[] loadApplications() {
	ArrayList<String> resps = new ArrayList<String>();
	HashMap<String,String> userAccounts = getUserAccounts();

	for (Iterator<Map.Entry<String, String>> entries = userAccounts.entrySet().iterator(); entries.hasNext(); ) {
		Map.Entry<String, String> entry = entries.next();
	    String url = entry.getKey();
		String project = entry.getValue();

		url = url.replace("XXX","applications?all=Y&");
		System.out.println(url);
		try {
			String res = httpGet(url);
			System.out.println("res="+res);
			resps.add(project);
			resps.add(res);
		} catch(Exception ex) {
			System.out.println("ex="+ex.getMessage());
		}
	}
	return resps.toArray(new String[resps.size()]);
    }
}
