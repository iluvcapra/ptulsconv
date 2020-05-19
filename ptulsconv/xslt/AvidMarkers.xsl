<?xml version="1.0" encoding="UTF-8"?>
<xsl:transform version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:fmp="http://www.filemaker.com/fmpxmlresult">

<xsl:output
    method="xml"
    standalone="no"
    doctype-system="AvidSettingsFile.dtd" />

<xsl:template match="/">
<Avid:StreamItems xmlns:Avid="http://www.avid.com">
<Avid:XMLFileData>
<AvProp name="DomainMagic" type="string">Domain</AvProp>
<AvProp name="DomainKey" type="char4">58424a44</AvProp>
<xsl:for-each select="/fmp:FMPXMLRESULT/fmp:RESULTSET/fmp:ROW">
<AvClass id="ATTR">
  <AvProp id="ATTR" name="__OMFI:ATTR:NumItems" type="int32">7</AvProp>
  <List id="OMFI:ATTR:AttrRefs">
    <ListElem>
      <AvProp id="ATTR" name="OMFI:ATTB:Kind" type="int32">1</AvProp>
      <AvProp id="ATTR" name="OMFI:ATTB:Name" type="string">_ATN_CRM_LONG_CREATE_DATE</AvProp>
      <AvProp id="ATTR" name="OMFI:ATTB:IntAttribute" type="int32">1570299854</AvProp>
    </ListElem>
    <ListElem>
      <AvProp id="ATTR" name="OMFI:ATTB:Kind" type="int32">2</AvProp>
      <AvProp id="ATTR" name="OMFI:ATTB:Name" type="string">_ATN_CRM_COLOR</AvProp>
      <AvProp id="ATTR" name="OMFI:ATTB:StringAttribute" type="string">yellow</AvProp>
    </ListElem>
    <ListElem>
      <AvProp id="ATTR" name="OMFI:ATTB:Kind" type="int32">2</AvProp>
      <AvProp id="ATTR" name="OMFI:ATTB:Name" type="string">_ATN_CRM_USER</AvProp>
      <AvProp id="ATTR" name="OMFI:ATTB:StringAttribute" type="string">
	<xsl:value-of select="fmp:COL[2]/fmp:DATA" /></AvProp>
    </ListElem>
    <ListElem>
      <AvProp id="ATTR" name="OMFI:ATTB:Kind" type="int32">2</AvProp>
      <AvProp id="ATTR" name="OMFI:ATTB:Name" type="string">_ATN_CRM_COM</AvProp>
      <AvProp id="ATTR" name="OMFI:ATTB:StringAttribute" type="string">
	<xsl:value-of select="concat('(',fmp:COL[14]/fmp:DATA,') ',fmp:COL[15]/fmp:DATA, ': ', fmp:COL[21]/fmp:DATA, ' ')"/>
        <xsl:choose>
          <xsl:when test="fmp:COL[18]/fmp:DATA != ''">[Reason: <xsl:value-of select="fmp:COL[18]/fmp:DATA" />]
          </xsl:when>
          <xsl:otherwise> </xsl:otherwise>
        </xsl:choose>
        <xsl:choose>
          <xsl:when test="fmp:COL[23]/fmp:DATA != ''">[Note: <xsl:value-of select="fmp:COL[23]/fmp:DATA" />]</xsl:when>
        </xsl:choose>
      </AvProp>
    </ListElem>
    <ListElem>
      <AvProp id="ATTR" name="OMFI:ATTB:Kind" type="int32">2</AvProp>
      <AvProp id="ATTR" name="OMFI:ATTB:Name" type="string">_ATN_CRM_TC</AvProp>
      <AvProp id="ATTR" name="OMFI:ATTB:StringAttribute" type="string">
	<xsl:value-of select="fmp:COL[11]/fmp:DATA" /></AvProp>
    </ListElem>
    <ListElem>
      <AvProp id="ATTR" name="OMFI:ATTB:Kind" type="int32">2</AvProp>
      <AvProp id="ATTR" name="OMFI:ATTB:Name" type="string">_ATN_CRM_TRK</AvProp>
      <AvProp id="ATTR" name="OMFI:ATTB:StringAttribute" type="string">V1</AvProp>
    </ListElem>
    <ListElem>
      <AvProp id="ATTR" name="OMFI:ATTB:Kind" type="int32">1</AvProp>
      <AvProp id="ATTR" name="OMFI:ATTB:Name" type="string">_ATN_CRM_LENGTH</AvProp>
      <AvProp id="ATTR" name="OMFI:ATTB:IntAttribute" type="int32">1</AvProp>
    </ListElem>
    <ListElem/>
  </List>
</AvClass>
</xsl:for-each>

</Avid:XMLFileData>
</Avid:StreamItems>

</xsl:template>

</xsl:transform>
