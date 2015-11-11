var analysis = {
    overview: {
        init: function(type) {
            $("#"+ type +"-container").addClass("loading");
            $.get( "/overview-async/", { "report_type": type }, function(data) {
                analysis.overview.appendPies(data, "#"+ type +"-container .charts-container");
                $("#"+ type +"-domain-cnt").html(data.domain_cnt);
                $("#"+ type +"-report-cnt").html(data.report_cnt);
                $("#"+ type +"-message-cnt").html(data.message_cnt);
                $("#"+ type +"-container .text-container").show();
            }).always(function() {
                $("#"+ type +"-container").removeClass("loading");
            });
        },
        appendPies: function(data, targetSelector) {
            ["dkim", "spf", "disposition"].forEach(function(type){
                var width = 200,
                    height = 200,
                    margin = {top: 50, left: 50},
                    radius = 90;

                var color;
                if (type == "disposition"){
                color = d3.scale.ordinal()
                    .domain(["reject", "quarantine", "none"])
                    .range(["#CC0000", "#CCCC00", "#00CC00"]);
                } else {
                color = d3.scale.ordinal()
                    .domain(["fail", "pass"])
                    .range(["#CC0000", "#00CC00"]);
                }

                var arc = d3.svg.arc()
                    .outerRadius(radius - 10)
                    .innerRadius(0);

                var pie = d3.layout.pie()
                    .sort(null)
                    .value(function(d) { return d.cnt; });

                var svg = d3.select(targetSelector).append("svg")
                    .attr("class", type)
                    .attr("width", width + margin.left)
                    .attr("height", height + margin.top)
                    .append("g")
                    .attr("transform", "translate(" + (width / 2 + margin.left) + "," + (height / 2 + margin.top) + ")");

                var g = svg.selectAll(".arc")
                    .data(pie(data[type]))
                    .enter().append("g")
                    .attr("class", "arc");

                g.append("path")
                   .attr("d", arc)
                   .style("fill", function(d) { return color(d.data.label); });

                g.append("text")
                    .attr("transform", "translate(0, -120)")
                    .text(type.toUpperCase());
                    
                var lineLegendOptions = {
                    legendItems : data[type].map(function(d){return {color: color(d.label), name: (d.cnt + " " + d.label)} })
                }
                g.append("g")
                  .attr("class", "legend")
                  .attr("transform", "translate(-120, -110)")
                  .style("font-size", "12px")
                  .call(d3.legend, lineLegendOptions); 
            });
        }
    },
    map : {
        _map: null,
        _dataSets : [],
        _mapDataSets: [],
        _width: null,
        _countryCodeMapping: {
            "AF": "AFG", "AL": "ALB", "DZ": "DZA", "AD": "AND", "AO": "AGO", "AG": "ATG", "AR": "ARG", "AM": "ARM", "AU": "AUS", "AT": "AUT", "AZ": "AZE", "BS": "BHS", "BH": "BHR", "BD": "BGD", "BB": "BRB", "BY": "BLR", "BE": "BEL", "BZ": "BLZ", "BJ": "BEN", "BT": "BTN", "BO": "BOL", "BA": "BIH", "BW": "BWA", "BR": "BRA", "BN": "BRN", "BG": "BGR", "BF": "BFA", "BI": "BDI", "KH": "KHM", "CM": "CMR", "CA": "CAN", "CV": "CPV", "CF": "CAF", "TD": "TCD", "CL": "CHL", "CO": "COL", "KM": "COM", "24": ",CD", "24": ",CG", "CR": "CRI", "CI": "CIV", "HR": "HRV", "CU": "CUB", "CY": "CYP", "CZ": "CZE", "DK": "DNK", "DJ": "DJI", "DM": "DMA", "DO": "DOM", "EC": "ECU", "EG": "EGY", "SV": "SLV", "GQ": "GNQ", "ER": "ERI", "EE": "EST", "ET": "ETH", "FJ": "FJI", "FI": "FIN", "FR": "FRA", "GA": "GAB", "22": ",GM", "GE": "GEO", "DE": "DEU", "GH": "GHA", "GR": "GRC", "GD": "GRD", "GT": "GTM", "GN": "GIN", "GW": "GNB", "GY": "GUY", "HT": "HTI", "HN": "HND", "HU": "HUN", "IS": "ISL", "IN": "IND", "ID": "IDN", "IR": "IRN", "IQ": "IRQ", "IE": "IRL", "IL": "ISR", "IT": "ITA", "JM": "JAM", "JP": "JPN", "JO": "JOR", "KZ": "KAZ", "KE": "KEN", "KI": "KIR", "KW": "KWT", "KG": "KGZ", "LA": "LAO", "LV": "LVA", "LB": "LBN", "LS": "LSO", "LR": "LBR", "LY": "LBY", "LI": "LIE", "LT": "LTU", "LU": "LUX", "MK": "MKD", "MG": "MDG", "MW": "MWI", "MY": "MYS", "MV": "MDV", "ML": "MLI", "MT": "MLT", "MH": "MHL", "MR": "MRT", "MU": "MUS", "MX": "MEX", "FM": "FSM", "MD": "MDA", "MC": "MCO", "MN": "MNG", "ME": "MNE", "MA": "MAR", "MZ": "MOZ", "MM": "MMR", "NA": "NAM", "NR": "NRU", "NP": "NPL", "NL": "NLD", "NZ": "NZL", "NI": "NIC", "NE": "NER", "NG": "NGA", "NO": "NOR", "OM": "OMN", "PK": "PAK", "PW": "PLW", "PA": "PAN", "PG": "PNG", "PY": "PRY", "PE": "PER", "PH": "PHL", "PL": "POL", "PT": "PRT", "QA": "QAT", "RO": "ROU", "RU": "RUS", "RW": "RWA", "KN": "KNA", "LC": "LCA", "VC": "VCT", "WS": "WSM", "SM": "SMR", "ST": "STP", "SA": "SAU", "SN": "SEN", "RS": "SRB", "SC": "SYC", "SL": "SLE", "SG": "SGP", "SK": "SVK", "SI": "SVN", "SB": "SLB", "SO": "SOM", "ES": "ESP", "LK": "LKA", "SD": "SDN", "SR": "SUR", "SZ": "SWZ", "SE": "SWE", "CH": "CHE", "SY": "SYR", "TJ": "TJK", "TZ": "TZA", "TH": "THA", "TL": "TLS", "TG": "TGO", "TO": "TON", "TT": "TTO", "TN": "TUN", "TR": "TUR", "TM": "TKM", "TV": "TUV", "UG": "UGA", "UA": "UKR", "AE": "ARE", "GB": "GBR", "US": "USA", "UY": "URY", "UZ": "UZB", "VU": "VUT", "VA": "VAT", "VE": "VEN", "VN": "VNM", "YE": "YEM", "ZM": "ZMB", "ZW": "ZWE", "GE": "GEO", "TW": "TWN", "AZ": "AZE", "CY": "CYP", "MD": "MDA", "SO": "SOM", "GE": "GEO", "AU": "AUS", "CX": "CXR", "CC": "CCK", "AU": "AUS", "HM": "HMD", "NF": "NFK", "NC": "NCL", "PF": "PYF", "YT": "MYT", "GP": "GLP", "GP": "GLP", "PM": "SPM", "WF": "WLF", "TF": "ATF", "PF": "PYF", "BV": "BVT", "CK": "COK", "NU": "NIU", "TK": "TKL", "GG": "GGY", "IM": "IMN", "JE": "JEY", "AI": "AIA", "BM": "BMU", "IO": "IOT", "VG": "VGB", "KY": "CYM", "FK": "FLK", "GI": "GIB", "MS": "MSR", "PN": "PCN", "SH": "SHN", "GS": "SGS", "TC": "TCA", "MP": "MNP", "PR": "PRI", "AS": "ASM", "UM": "UMI", "GU": "GUM", "UM": "UMI", "UM": "UMI", "UM": "UMI", "UM": "UMI", "UM": "UMI", "UM": "UMI", "UM": "UMI", "VI": "VIR", "UM": "UMI", "HK": "HKG", "MO": "MAC", "FO": "FRO", "GL": "GRL", "GF": "GUF", "GP": "GLP", "MQ": "MTQ", "RE": "REU", "AX": "ALA", "AW": "ABW", "AN": "ANT", "SJ": "SJM", "AC": "ASC", "TA": "TAA", "AQ": "ATA", "AQ": "ATA", "CN": "CHN"
        },
        _defaults: {
            defaultFill: "white",
            defaultBorderColor: "darkgrey",
            defaultBorderWidth: 0.5,
            defaultBorderHoverWidth: 1
        },
        /*
         * Creates an array of `n` colors around the baseColor,
         * ranging the HSL lightness value from 0.1 to 0.9
         * 
         * cf. "Color Use Guidelines for Mapping and Visualization",
         * Brewer (sequential scheme, one hue)
         */
        createColorRange: function(baseColor, n) {
            var colorHsl = d3.hsl(baseColor),
                minL = 0.1,
                maxL = 0.9;
            var stepSize = (maxL - minL) / n;
            var colors = [];
            for (var i = 0; i < n; i++ ){
                colorHsl.l = maxL - (i*stepSize)
                colors.push(colorHsl.toString());
                }
            return colors;
        },
        /*
         * Draw map
         */
        init: function(viewId) {

            $(".view-type-map .svg-container").addClass("loading");
            d3.json("/map-async/" + viewId + "/", function(error, json) {
                $(".view-type-map .svg-container").removeClass("loading");
                if (error || json.length < 1) {
                    console.warn(error);
                    return false;
                } 

                analysis.map._dataSets = json;
                analysis.map._width    = $(".view-type .svg-container").width();
                
                // Transform server data for map plugin
                analysis.map._dataSets.forEach(function(dataSet, idx){

                    // Get message maximum
                    var max = d3.max(dataSet.data.map(function(obj) {
                        return obj.cnt;
                    }));

                    // Define color range with 5 colors
                    var colors = analysis.map.createColorRange(dataSet.color, 4)
                    var paletteScale = d3.scale.quantize()
                        .domain([1, max])
                        .range(colors);

                    // Create data for dataset
                    var data = {} // {"iso_code" : {"fillKey": <key>, "count": <cnt>}, ..}

                    dataSet.data.forEach(function(obj){
                        var color = paletteScale(obj.cnt) || colors[colors.length - 1]
                        data[analysis.map._countryCodeMapping[obj.country_iso_code]] = { count: obj.cnt, fillKey: color };
                    }); 

                    // Create fills and legend labels
                    var fills = {
                        defaultFill: analysis.map._defaults.defaultFill
                    };

                    var legendLabels = [];
                    colors.forEach(function(color){
                        fills[color] = color;
                        var extents = paletteScale.invertExtent(color);
                        legendLabels.push( {
                            color : color,
                            name  : Math.round(extents[0]) + " - " + Math.round(extents[1])
                        } );
                    });

                    // Store 
                    analysis.map._mapDataSets.push({ 
                        fills:     fills,
                        labels:    legendLabels,
                        data:      data
                    });

                    //Create and append button for each dataset
                    var $mapDataSetBtn = $("<button>", {class: "btn btn-default", value: idx, text: dataSet.label});
                    $(".view-type-map .btn-group").append($mapDataSetBtn);
                })

                // Init the map with no data
                analysis.map._map = new Datamap({
                    element: $(".view-type-map .svg-container").get(0),
                    projection: 'mercator',
                    width:  analysis.map._width,
                    height: analysis.map._width / 5 * 3, // keep a 5:3 ratio
                    geographyConfig: {
                        borderColor:            analysis.map._defaults.defaultBorderColor,
                        borderWidth:            analysis.map._defaults.defaultBorderWidth,
                        highlightFillColor:     analysis.map._defaults.defaultFill,
                        highlightBorderColor:   analysis.map._defaults.defaultBorderColor,
                        highlightBorderWidth:   analysis.map._defaults.defaultBorderHoverWidth,
                        popupTemplate: function(geo, data) {
                                        text = geo.properties.name + ": " + 
                                                (data ? data.count : "no") +
                                                " messages"
                                        $hoverInfo = $("<div>", {"class": "hoverinfo", "text": text})
                                        return $hoverInfo.prop('outerHTML');
                                    }
                    },
                    done: function(map) {
                        //Enable zooming and panning
                        map.svg.call(d3.behavior.zoom().on("zoom", function(){
                            //Don't zoom or pan no-resize classed elements (like legend)
                            map.svg.selectAll("g:not(.no-resize)")
                                .attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
                        }));
                    },
                    fills: {defaultFill : analysis.map._defaults.defaultFill}
                });

                // Update the map and legend with data on button click
                $(".view-type-map .btn-group button").on('click', function(e){
                    analysis.map.update(this);
                });
                // Trigger first button to be clicked
                $(".view-type-map .btn-group button:first-child").click();
            });
        },

        /*
         * Fill map with data and draw legend
         */
        update: function(elem){

            // Toggle button active
            $(elem).siblings().removeClass('active')
            $(elem).addClass('active');

            // Get data at button val index
            var data  = analysis.map._mapDataSets[$(elem).val()];
            var label = analysis.map._dataSets[$(elem).val()].label;

            // Reset fills and info directly on svg
            $(".view-type-map .datamaps-subunits path[data-info]")
                .css({fill: analysis.map._defaults.defaultFill})
                .attr("data-info", null);

            // Set new fills on map object
            analysis.map._map.options.fills = data.fills;

            // Update Choropleth
            analysis.map._map.updateChoropleth(data.data);

            // Update legend (custom legend plugin)
            var mapLegendOptions = {
                legendItems : data.labels.map(function(item){
                    return {color : item.color, name: item.name + " msgs"}
                })
            }
            // Remove old and add new legend
            analysis.map._map.svg.selectAll("g.legend").remove();
            analysis.map._map.svg.append("g")
                .attr("class", "legend no-resize")
                .attr("transform","translate(20,20)")
                .call(d3.legend, mapLegendOptions)
                .selectAll("g")
                .attr("class", "no-resize");

            // Remove old and add new title
            analysis.map._map.svg.selectAll(".map-title").remove();
            analysis.map._map.svg.append("text")
                .attr("class", "map-title")
                .attr("text-anchor", "middle")
                .attr("transform", "translate("+ (analysis.map._width / 2) + ", 30)")
                .style("font-weight", "bold")
                .text("Messages per time for '"+ label +"'");
        }
    },
    line: {
        _data : null,
        _dataSetsLine : null,
        _defaults : {
            margin : {
                top: 40, 
                right: 60, 
                bottom: 120, 
                left: 60
            },
            marginMini : {
                top: 430,
                right: 60,
                bottom: 20,
                left: 60
            }
        },
        init: function(viewId) {
            $(".view-type-linechart .svg-container").addClass("loading");
            d3.json("/line-async/" + viewId + "/", function(error, json) {
                $(".view-type-linechart .svg-container").removeClass("loading");
                if (error || json.length < 1) {
                    console.warn(error);
                    return false;
                }  

                analysis.line._data = json;
                // Create date format praser
                var parseDate = d3.time.format("%Y%m%d").parse;

                var dataSetsLine = analysis.line._data.data_sets;
                var begin    = parseDate(analysis.line._data.begin);
                var end      = parseDate(analysis.line._data.end);

                var clientWidth  = $(".view-type .svg-container").width();
                var clientHeight = 500;

                // Create margins, heights, widths for both plots
                var width      = clientWidth - analysis.line._defaults.margin.left - analysis.line._defaults.margin.right,
                    height     = clientHeight - analysis.line._defaults.margin.top - analysis.line._defaults.margin.bottom,
                    heightMini = clientHeight - analysis.line._defaults.marginMini.top - analysis.line._defaults.marginMini.bottom;

                // Ranges for both plots
                var x = d3.time.scale().range([0, width]),
                    y = d3.scale.linear().range([height, 0]),
                    xMini = d3.time.scale().range([0, width]),
                    yMini = d3.scale.linear().range([heightMini, 0]);

                // Axis for both plots
                var xAxis = d3.svg.axis().scale(x).orient("bottom"),
                    yAxis = d3.svg.axis().scale(y).orient("left"),
                    xAxisMini = d3.svg.axis().scale(xMini).orient("bottom");

                // Grid lines
                var xGridLines = d3.svg.axis().scale(x)
                                    .orient("bottom")
                                    .tickSize(-height, 0, 0)
                                    .tickFormat("");
                var yGridLines = d3.svg.axis().scale(y)
                                    .orient("left")
                                    .tickSize(-width, 0, 0)
                                    .tickFormat("");

                // Moving brush in mini chart changes chart domain
                var brush = d3.svg.brush()
                    .x(xMini)
                    .on("brush", function() { 
                        x.domain(brush.empty() ? xMini.domain() : brush.extent());
                        focus.selectAll(".line").attr("d", line);
                        focus.select(".x.axis").call(xAxis);
                        focus.select(".x.grid").call(xGridLines);

                        // XXX LP: Inline not so nice, but problem with export, maybe use css inliner on export
                        svg.selectAll(".grid .tick")
                            .style("stroke", "#DADADA");
                        svg.selectAll(".tick text")
                            .style("font-size", "10px");
                    })
                    .on("brushend", function(){
                        analysis.table.addDateTimeFilter(x.domain());
                    });

                //Append svg to document
                var svg = d3.select(".view-type-linechart .svg-container").append("svg")
                    .attr("width", width + analysis.line._defaults.margin.left + analysis.line._defaults.margin.right)
                    .attr("height", height + analysis.line._defaults.margin.top + analysis.line._defaults.margin.bottom);
        
                //Define a viewport, so that the line does not move over axis
                //This does not work when exported
                svg.append("defs").append("clipPath")
                    .attr("id", "clip")
                  .append("rect")
                    .attr("width", width)
                    .attr("height", clientHeight);
        
                // Append main chart to svg and place it
                var focus = svg.append("g")
                    .attr("class", "focus")
                    .attr("transform", "translate(" + analysis.line._defaults.margin.left + "," + analysis.line._defaults.margin.top + ")");
        
                // Append overview chart to svg and place it 
                var context = svg.append("g")
                    .attr("class", "context")
                    .attr("transform", "translate(" + analysis.line._defaults.marginMini.left + "," + analysis.line._defaults.marginMini.top + ")");
        
                // Create main chart line generator
                var line = d3.svg.line()
                    .x(function(d) { return x(d.date); })
                    .y(function(d) { return y(d.cnt); });
        
                // Create overview chart line generator
                var lineMini = d3.svg.line()
                    .x(function(d) { return xMini(d.date); })
                    .y(function(d) { return yMini(d.cnt); });

                // Convert date strings to dates
                dataSetsLine.forEach(function(dataSet){
                  dataSet.data.forEach(function(obj){
                    obj.date = parseDate(obj.date);
                  })
                })
        
                //Create 0 data points for days of range that are not in the dataset
                //data MUST be orderd by date
                var days = d3.time.day.range(begin, end);
                dataSetsLine.forEach(function(dataSet){
                    data_len = dataSet.data.length;
                    data_tmp = [];
                    var j = 0;
                    for (var i = 0; i < days.length; i++) {
                        // + for number cast
                        if ((data_len > j) && (+days[i] == +dataSet.data[j].date)){
                            cnt = dataSet.data[j].cnt; 
                            j += 1;
                        } else {
                            cnt = 0;
                        }
                        data_tmp.push({date: days[i], cnt: cnt});
                    }
                    dataSet.data = data_tmp
                });
        
                x.domain([begin, end]);
        
                // Get max value by traversing all datasets' data lists
                y.domain(
                  [0, d3.max([].concat.apply([], 
                    dataSetsLine.map(function(dataSet){
                        return dataSet.data.map(
                            function(d){
                                return d.cnt;
                            })
                    })))]);
        
                // Get the domains for x and y values for overview chart
                xMini.domain(x.domain());
                yMini.domain(y.domain());
        
                // Create the actual lines and append to svg
                dataSetsLine.forEach(function(dataSet, idx) {
                  // for main chart
                  focus.append("path")
                      .datum(dataSet.data)
                      .attr("class", "line")
                      .attr("d", line)
                      .attr("stroke", dataSet.color);
                  // and for mini chart
                  context.append("path")
                      .datum(dataSet.data)
                      .attr("class", "line")
                      .attr("d", lineMini)
                      .attr("stroke", dataSet.color);
                });
        
                // Append X Axis for main chart
                focus.append("g")
                    .attr("class", "x axis")
                    .attr("transform", "translate(0," + height + ")")
                    .call(xAxis);
        
                // Append Y Axis for main chart
                focus.append("g")
                    .attr("class", "y axis")
                    .call(yAxis);
        
                // prepend gridlines, so they are under the lines 
                focus.insert("g", ":first-child")
                    .attr("class", "x grid")
                    .attr("transform", "translate(0," + height + ")")
                    .call(xGridLines);
                focus.insert("g", ":first-child")
                    .attr("class", "y grid")
                    .call(yGridLines);
        
        
                svg.append("text")
                    .attr("class", "y label")
                    .attr("transform", "rotate(-90)translate(" + (height/2 * -1 ) + ", "+ (analysis.line._defaults.margin.left / 2 - 5)+")")
                    .text("Message count");
        
                // Append X Axis for mini chart
                context.append("g")
                    .attr("class", "x axis")
                    .attr("transform", "translate(0," + heightMini + ")")
                    .call(xAxisMini);
        
                // Append the moving window for the mini chart
                context.append("g")
                    .attr("class", "x brush")
                    .call(brush)
                  .selectAll("rect")
                    .attr("y", -6)
                    .attr("height", heightMini + 7);
        
                // CSS inline hack for SVG export support
                svg.selectAll(".brush .extent")
                    .style("stroke", "#fff")
                    .style("fill-opacity", .125)
                    .style("shape-rendering", "crispEdges");
                svg.selectAll(".label")
                    .style("text-anchor", "middle");
                svg.selectAll("path")
                    .style("stroke-width", 2)
                    .style("fill", "none")
                    .style("clip-path", "url(#clip)");
                svg.selectAll("rect")
                    .style("stroke-width", 2)
                svg.selectAll(".axis path, .axis line")
                    .style("fill", "none")
                    .style("stroke", "#DADADA")
                    .style("stroke-width", 1)
                    .style("shape-rendering", "crispEdges");
                svg.selectAll(".grid .tick")
                    .style("stroke", "#DADADA");    
                svg.selectAll(".tick text")
                    .style("font-size", "10px")
                svg.selectAll(".grid path")
                    .style("stroke-width", 0);

                // Add legend
                focus.append("g")
                    .attr("class", "legend")
                    .attr("transform", "translate(20,20)")
                    .call(d3.legend, {
                        legendItems : dataSetsLine.map(function(d){
                                                            return {
                                                                color: d.color, 
                                                                name: d.label
                                                            } 
                                                        })
                }); 
        
                // Add title
                svg.append("text")
                    .attr("text-anchor", "middle")
                    .attr("transform", "translate("+ (clientWidth / 2) + ", " + (analysis.line._defaults.margin.top / 2) +")")
                    .style("font-weight", "bold")
                    .text("Messages over time");
            });
        }
    },
    table: {
        _api: null,
        _tableTimes: [],
        addDateTimeFilter: function(dateTimes) {
            var formatDate = d3.time.format("%Y-%m-%d");
            $filterContainer = $("#time-quick-filter-date");
            if ($filterContainer)
                $filterContainer.html(
                    "Filtering from <strong>" 
                    + formatDate(dateTimes[0]) 
                    + "</strong> to <strong>" + 
                    formatDate(dateTimes[1]) + "</strong");

                analysis.table._tableTimes = dateTimes;
                analysis.table._api.ajax.reload();
        },
        init: function(viewId) {
            analysis.table._api = $('.view-type-table table').DataTable({
                "ajax" : {
                    url  : "/table-async/" + viewId + "/",
                    type : "POST",
                    data: function (data) {
                         data["custom_filters"] = {
                            "time" : analysis.table._tableTimes // Does this newly read variable every time?
                         }
                         return { 
                            "data" : JSON.stringify(data),
                          };
                    },
                },
                "searching": false,
                "serverSide": true,
                "processing": true,
                "language": {
                    "processing": ""
                }
            })
        }
    },
    export: {
        svg: function(viewId, btn) {
            var svg_node = $(btn).closest(".view-type").find(".svg-container svg").get(0)
            $('<form>', {
                'action': "/export-svg/"+viewId+"/",
                'target': "_blank",
                'method': "POST"
            }).append($('<textarea>', {
                'name': "svg",
                'value': (new XMLSerializer).serializeToString(svg_node),
            })).append($('<input>', {
                'type': 'hidden',
                'name': 'csrfmiddlewaretoken',
                'value': getCookie('csrftoken'),
            })).submit();
            // One should know that input field text is limited to 512KB length
        },
        csv: function(viewId) {
            $('<form>', {
                'action': "/export-csv/"+viewId+"/",
                'target': "_blank",
                'method': "POST"
            }).append($('<input>', {
                'type': 'hidden',
                'name': 'csrfmiddlewaretoken',
                'value': getCookie('csrftoken'),
            })).submit();  
            getCookie
        },
    }
}

