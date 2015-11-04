// d3.legend.js 
// (C) 2012 ziggy.jonsson.nyc@gmail.com
// MIT licence
// XXX LP: Customized for my needs

(function() {
    d3.legend = function(g, options) {
        // options format
        // {legendItems : [{color: <color>, name: <name>},..]}
        g.each(function() {
            
            var g = d3.select(this),
                legendPadding = 5,
                radius = 5,
                lBox = g.selectAll(".legend-box").data([true]),
                lItems = g.selectAll(".legend-items").data([true])
            
            lBox.enter().append("rect").classed("legend-box",true)
            lItems.enter().append("g").classed("legend-items",true)       

            lBox.style('fill', 'white')
                .style('stroke', 'black');

            lItems.selectAll("text")
                .data(options.legendItems)
                .call(function(d) { d.enter().append("text")})
                .call(function(d) { d.exit().remove()})
                .attr("transform", function(d, i){
                    return "translate(" + radius * 2 + ", "+ i * 2 * radius +")"
                })
                .text(function(d) {return d.name})
            
            lItems.selectAll("circle")
                .data(options.legendItems)
                .call(function(d) { d.enter().append("circle")})
                .call(function(d) { d.exit().remove()})
                .attr("transform", function(d, i){
                    return "translate(0, "+ ((i * 2 * radius) - radius) +")"
                })
                .attr("r", radius)
                .style("fill", function(d) {return d.color})  

            // Reposition and resize the box
            var lbbox = lItems[0][0].getBBox()  
            lBox.attr("x",(lbbox.x-legendPadding))
                .attr("y",(lbbox.y-legendPadding))
                .attr("height",(lbbox.height+2*legendPadding))
                .attr("width",(lbbox.width+2*legendPadding))
      })
      return g
}
})()

// XXX LP: Only temp, don't worry. Also incomplete :)
var countryCodeMapping = {"AF": "AFG", "AL": "ALB", "DZ": "DZA", "AD": "AND", "AO": "AGO", "AG": "ATG", "AR": "ARG", "AM": "ARM", "AU": "AUS", "AT": "AUT", "AZ": "AZE", "BS": "BHS", "BH": "BHR", "BD": "BGD", "BB": "BRB", "BY": "BLR", "BE": "BEL", "BZ": "BLZ", "BJ": "BEN", "BT": "BTN", "BO": "BOL", "BA": "BIH", "BW": "BWA", "BR": "BRA", "BN": "BRN", "BG": "BGR", "BF": "BFA", "BI": "BDI", "KH": "KHM", "CM": "CMR", "CA": "CAN", "CV": "CPV", "CF": "CAF", "TD": "TCD", "CL": "CHL", "CO": "COL", "KM": "COM", "24": ",CD", "24": ",CG", "CR": "CRI", "CI": "CIV", "HR": "HRV", "CU": "CUB", "CY": "CYP", "CZ": "CZE", "DK": "DNK", "DJ": "DJI", "DM": "DMA", "DO": "DOM", "EC": "ECU", "EG": "EGY", "SV": "SLV", "GQ": "GNQ", "ER": "ERI", "EE": "EST", "ET": "ETH", "FJ": "FJI", "FI": "FIN", "FR": "FRA", "GA": "GAB", "22": ",GM", "GE": "GEO", "DE": "DEU", "GH": "GHA", "GR": "GRC", "GD": "GRD", "GT": "GTM", "GN": "GIN", "GW": "GNB", "GY": "GUY", "HT": "HTI", "HN": "HND", "HU": "HUN", "IS": "ISL", "IN": "IND", "ID": "IDN", "IR": "IRN", "IQ": "IRQ", "IE": "IRL", "IL": "ISR", "IT": "ITA", "JM": "JAM", "JP": "JPN", "JO": "JOR", "KZ": "KAZ", "KE": "KEN", "KI": "KIR", "KW": "KWT", "KG": "KGZ", "LA": "LAO", "LV": "LVA", "LB": "LBN", "LS": "LSO", "LR": "LBR", "LY": "LBY", "LI": "LIE", "LT": "LTU", "LU": "LUX", "MK": "MKD", "MG": "MDG", "MW": "MWI", "MY": "MYS", "MV": "MDV", "ML": "MLI", "MT": "MLT", "MH": "MHL", "MR": "MRT", "MU": "MUS", "MX": "MEX", "FM": "FSM", "MD": "MDA", "MC": "MCO", "MN": "MNG", "ME": "MNE", "MA": "MAR", "MZ": "MOZ", "MM": "MMR", "NA": "NAM", "NR": "NRU", "NP": "NPL", "NL": "NLD", "NZ": "NZL", "NI": "NIC", "NE": "NER", "NG": "NGA", "NO": "NOR", "OM": "OMN", "PK": "PAK", "PW": "PLW", "PA": "PAN", "PG": "PNG", "PY": "PRY", "PE": "PER", "PH": "PHL", "PL": "POL", "PT": "PRT", "QA": "QAT", "RO": "ROU", "RU": "RUS", "RW": "RWA", "KN": "KNA", "LC": "LCA", "VC": "VCT", "WS": "WSM", "SM": "SMR", "ST": "STP", "SA": "SAU", "SN": "SEN", "RS": "SRB", "SC": "SYC", "SL": "SLE", "SG": "SGP", "SK": "SVK", "SI": "SVN", "SB": "SLB", "SO": "SOM", "ES": "ESP", "LK": "LKA", "SD": "SDN", "SR": "SUR", "SZ": "SWZ", "SE": "SWE", "CH": "CHE", "SY": "SYR", "TJ": "TJK", "TZ": "TZA", "TH": "THA", "TL": "TLS", "TG": "TGO", "TO": "TON", "TT": "TTO", "TN": "TUN", "TR": "TUR", "TM": "TKM", "TV": "TUV", "UG": "UGA", "UA": "UKR", "AE": "ARE", "GB": "GBR", "US": "USA", "UY": "URY", "UZ": "UZB", "VU": "VUT", "VA": "VAT", "VE": "VEN", "VN": "VNM", "YE": "YEM", "ZM": "ZMB", "ZW": "ZWE", "GE": "GEO", "TW": "TWN", "AZ": "AZE", "CY": "CYP", "MD": "MDA", "SO": "SOM", "GE": "GEO", "AU": "AUS", "CX": "CXR", "CC": "CCK", "AU": "AUS", "HM": "HMD", "NF": "NFK", "NC": "NCL", "PF": "PYF", "YT": "MYT", "GP": "GLP", "GP": "GLP", "PM": "SPM", "WF": "WLF", "TF": "ATF", "PF": "PYF", "BV": "BVT", "CK": "COK", "NU": "NIU", "TK": "TKL", "GG": "GGY", "IM": "IMN", "JE": "JEY", "AI": "AIA", "BM": "BMU", "IO": "IOT", "VG": "VGB", "KY": "CYM", "FK": "FLK", "GI": "GIB", "MS": "MSR", "PN": "PCN", "SH": "SHN", "GS": "SGS", "TC": "TCA", "MP": "MNP", "PR": "PRI", "AS": "ASM", "UM": "UMI", "GU": "GUM", "UM": "UMI", "UM": "UMI", "UM": "UMI", "UM": "UMI", "UM": "UMI", "UM": "UMI", "UM": "UMI", "VI": "VIR", "UM": "UMI", "HK": "HKG", "MO": "MAC", "FO": "FRO", "GL": "GRL", "GF": "GUF", "GP": "GLP", "MQ": "MTQ", "RE": "REU", "AX": "ALA", "AW": "ABW", "AN": "ANT", "SJ": "SJM", "AC": "ASC", "TA": "TAA", "AQ": "ATA", "AQ": "ATA", "CN": "CHN"};