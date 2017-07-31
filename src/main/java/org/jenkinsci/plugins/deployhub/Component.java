package org.jenkinsci.plugins.deployhub;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

import org.kohsuke.stapler.bind.JavaScriptMethod;

import hudson.Extension;

@Extension
public class Component extends Common {
    String compname;
    String basename;

    public String getIconFileName() {
        return "/plugin/deployhub/images/application.png";
    }

    public Component(String compname) {
	int p = compname.lastIndexOf(".");
	this.compname = compname;
	this.basename = (p>=0)?compname.substring(p+1):compname;
    }

    public Component() {
    }

    public String getDisplayName() {
	return basename;
    }

@JavaScriptMethod
    public String[] loadComponent() {
	ArrayList<String> resps = new ArrayList<String>();
	HashMap<String,String> userAccounts = getUserAccounts();

	for (Iterator<Map.Entry<String, String>> entries = userAccounts.entrySet().iterator(); entries.hasNext(); ) {
		Map.Entry<String, String> entry = entries.next();
	    String url = entry.getKey();
		String project = entry.getValue();

		url = url.replace("XXX","component/"+compname+"?").replace(" ","%20");
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
