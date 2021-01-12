<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!--  the number of items to include in each group -->
    <xsl:template match="/">
        <xsl:apply-templates select="//item[position() mod 3 = 1]" />
    </xsl:template>
    <xsl:template match="item" mode="inner">
        <!-- handle items appropriately here -->
        <div class="col-md-4 align-items-center" style="min-width: 0;
                                                    word-wrap: break-word;
                                                    background-color: #fff;
                                                    background-clip: border-box;
                                                    border: 1px solid rgba(0, 0, 0, 0.125);
                                                    border-radius: 0.25rem;
                                                    border-bottom-right-radius: 0.25rem;
                                                    border-bottom-left-radius: 0.25rem;">
            <br/>
            <img>

                <xsl:attribute name="style">"width: 60%; height: 60%"</xsl:attribute>
                <xsl:attribute name="src"><xsl:value-of xmlns:media="http://search.yahoo.com/mrss/"
              select="media:content/@url"/></xsl:attribute>


                <xsl:attribute name="alt">Card image cap</xsl:attribute>
                <xsl:attribute name="class">card-img-top</xsl:attribute>
            </img>
            <br/>
            <h2>
                <a> <xsl:attribute name="href"><xsl:value-of select="link"/></xsl:attribute>
                    <xsl:value-of select="title"/>
                </a>
            </h2><br/>
            <!--<xsl:value-of select="description"/>-->
            <div class="card-footer text-muted">
                <xsl:value-of select="pubDate"/><br/></div>
        </div>
    </xsl:template>
    <xsl:template match="item">
        <div class="row">
            <br/><br/>
            <xsl:apply-templates select=".|following-sibling::item[position() > 3]" mode="inner" />
        </div>
    </xsl:template>
</xsl:stylesheet>