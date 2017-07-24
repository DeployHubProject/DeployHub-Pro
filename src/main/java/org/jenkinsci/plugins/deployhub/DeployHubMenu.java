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
        return (DeployHubMenuDescriptor) Jenkins.getInstance().getDescriptorOrDie(getClass());
    }

    public static ExtensionList<DeployHubMenu> all() {
        return Jenkins.getInstance().getExtensionList(DeployHubMenu.class);
    }
}
