<?xml version="1.0" encoding="UTF-8"?>
<xsl:transform version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
               xmlns:fmp="http://www.filemaker.com/fmpxmlresult">

<xsl:output method="text" encoding="windows-1252"/>
<xsl:template match="/">

<xsl:for-each select="/fmp:FMPXMLRESULT/fmp:RESULTSET/fmp:ROW">
	<xsl:sort data-type="number" select="number(fmp:COL[9]/fmp:DATA)" />
<xsl:value-of select="concat(position() ,'&#xA;')" />
	<xsl:value-of select="concat(format-number(floor(number(fmp:COL[9]/fmp:DATA) div 3600),'00'), ':')" />
	<xsl:value-of select="concat(format-number(floor(number(fmp:COL[9]/fmp:DATA) div 60),'00'), ':')" />
	<xsl:value-of select="concat(format-number(floor(number(fmp:COL[9]/fmp:DATA) mod 60),'00'), ',')" />
	<xsl:value-of select="format-number((number(fmp:COL[9]/fmp:DATA) - floor(number(fmp:COL[9]/fmp:DATA))) * 1000,'000')" />
	<xsl:text> --> </xsl:text>

	<xsl:value-of select="concat(format-number(floor(number(fmp:COL[10]/fmp:DATA) div 3600),'00'), ':')" />
	<xsl:value-of select="concat(format-number(floor(number(fmp:COL[10]/fmp:DATA) div 60),'00'), ':')" />
	<xsl:value-of select="concat(format-number(floor(number(fmp:COL[10]/fmp:DATA) mod 60),'00'), ',')" />
	<xsl:value-of select="format-number((number(fmp:COL[10]/fmp:DATA) - floor(number(fmp:COL[10]/fmp:DATA))) * 1000,'000')" />

	<xsl:value-of select="concat('&#xA;',fmp:COL[15]/fmp:DATA, ': ', fmp:COL[21]/fmp:DATA)"/>
	<xsl:value-of select="'&#xA;&#xA;'" />

</xsl:for-each>
</xsl:template>


</xsl:transform>