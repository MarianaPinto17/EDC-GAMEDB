<?xml version="1.0" encoding="utf-8" ?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="">
    <xsl:template match="/">
        <xsl:for-each select="/games/game">
            <!-- Page Content -->

            <div class="d-flex flex-row" style="min-width: 0;
                                                word-wrap: break-word;
                                                background-color: #fff;
                                                background-clip: border-box;
                                                border: 1px solid rgba(0, 0, 0, 0.125);
                                                border-radius: 0.25rem;
                                                border-bottom-right-radius: 0.25rem;
                                                border-bottom-left-radius: 0.25rem;
                                                margin-bottom: 1.5rem !important;
                                                padding-block: 2%">
                <div class="p-2" style="padding-left: 7% !important">
                    <!--<img class="card-img-top" src="" alt="Card image cap"/>-->
                    <img>
                        <xsl:attribute name="src">
                            <xsl:value-of select="gallery/header/image/full_size"/>
                        </xsl:attribute>
                        <xsl:attribute name="alt">"Card image cap"</xsl:attribute>
                        <xsl:attribute name="class">"card-img-top"</xsl:attribute>
                    </img>

                </div>
                <div class="p-2">
                    <!--<div class="card-body" style="align-items: baseline">-->
                    <p style="font-size:30px">
                        <a>
                            <xsl:attribute name="href">/game/<xsl:value-of select="@id"/>/</xsl:attribute>
                            <xsl:value-of select="title"/>
                        </a>
                    </p>
                    <p>Price: <xsl:variable name="price_now" select="price"/>
                        <xsl:choose>
                            <xsl:when test="not(contains($price_now, 'Free'))">
                                 <xsl:value-of select="$price_now"/><xsl:text>$</xsl:text>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:value-of select="$price_now"/>
                            </xsl:otherwise>
                        </xsl:choose>

                    </p>

                    <p> Release Date: <xsl:value-of select="release-date"/></p>
                    <xsl:variable name="cat">
                        <xsl:for-each select="genres/genre">
                            <xsl:text>|</xsl:text>
                            <xsl:value-of select="."/>
                            <xsl:text>| </xsl:text>
                        </xsl:for-each>
                    </xsl:variable>
                    <p> Genres:

                        <xsl:value-of select="$cat"/>
                        <xsl:for-each select="tags/tag">
                            <xsl:variable name="now">
                                <xsl:value-of select="."/>
                            </xsl:variable>
                            <xsl:if test="not(contains($cat,$now))">
                                    <xsl:text>|</xsl:text>
                                    <xsl:value-of select="."/>
                                    <xsl:text>| </xsl:text>
                            </xsl:if>

                        </xsl:for-each>


                    </p>
                    <!--</div>-->
                </div>
                <!--
                <div class="card-footer text-muted">
                    Posted on January 1, 2017 by
                    <a href="#">Start Bootstrap</a>
                </div>
                -->
            </div>

        </xsl:for-each>
    </xsl:template>

</xsl:stylesheet>