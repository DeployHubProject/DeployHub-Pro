package org.jenkinsci.plugins.deployhub;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

import org.kohsuke.stapler.bind.JavaScriptMethod;

import hudson.Extension;

@Extension
public class Application extends Common {
    String appname;
    String basename;

    public String getIconFileName() {
        return "/plugin/deployhub/images/application.png";
    }

    public Application(String appname) {
	int p = appname.lastIndexOf(".");
	this.appname = appname;
	this.basename = (p>=0)?appname.substring(p+1):appname;
    }

    public Application() {
	System.out.println("Application constructor called with no id");
    }

    public String getDisplayName() {
	return basename;
    }

@JavaScriptMethod
    public String[] loadApplication() {
	ArrayList<String> resps = new ArrayList<String>();
	HashMap<String,String> userAccounts = getUserAccounts();
	for (Iterator<Map.Entry<String, String>> entries = userAccounts.entrySet().iterator(); entries.hasNext(); ) {
		Map.Entry<String, String> entry = entries.next();
	    String url = entry.getKey();
		String project = entry.getValue();
		url = url.replace("XXX","application/"+appname+"?").replace(" ","%20");
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
