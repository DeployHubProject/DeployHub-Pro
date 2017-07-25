package org.jenkinsci.plugins.deployhub;

import hudson.ExtensionList;
import hudson.ExtensionPoint;
import hudson.model.Action;
import hudson.model.Describable;

import jenkins.model.Jenkins;

public abstract class DeployHubMenu implements ExtensionPoint, Action, Describable<DeployHubMenu> {
    public String getIconFileName() {
        return "gear.png";
    }

    public String getUrlName() {
        return getClass().getSimpleName();
    }

    public String getDisplayName() {
        return getClass().getSimpleName();
    }

    public abstract String getDescription();

    public DeployHubMenuDescriptor getDescriptor() {
        Jenkins jenkins = Jenkins.getInstance();
        if (jenkins == null)
         return null;
        
        return (DeployHubMenuDescriptor) jenkins.getDescriptorOrDie(getClass());
    }

    public static ExtensionList<DeployHubMenu> all() {
        Jenkins jenkins = Jenkins.getInstance();
        if (jenkins == null)
         return null;
        
        return jenkins.getExtensionList(DeployHubMenu.class);
    }
}
