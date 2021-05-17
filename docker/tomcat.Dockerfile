FROM woahbase/alpine-tomcat

ENTRYPOINT ["/opt/tomcat/bin/catalina.sh", "run"]