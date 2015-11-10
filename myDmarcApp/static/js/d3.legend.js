
/*
d3.legend.js 
(C) 2012 ziggy.jonsson.nyc@gmail.com
MIT licence
XXX LP: Customized for my needs
 
 Simple legend 
------------------------
|  [c1] text1          |
|  [c2] text2          |
|  [c3] textLong3      |
––––––––––––––––––––––––
 Variables 
    padding of cell box
    font items
    space befor item
    space between color and text
    circle adjusts with text

 Options:
    {
        legendItems : [{color: <color>, name: <name>},..]
    }
*/

(function() {
    d3.legend = function(g, options) {
        g.each(function() {
                        
            var g = d3.select(this),
               lBox     = g.selectAll(".legend-box").data([true]),
               lItems   = g.selectAll(".legend-items").data([true]);
           
            // Style options
            var boxPadding = 10,
                fontItem    = {size: 12},
                spaceItemV = 5,
                spaceItemH = 10;
    
            //calculate
            var radius = fontItem.size / 2;
            
            lBox.enter().append("rect").classed("legend-box",true);
            lItems.enter().append("g").classed("legend-items",true);

            lBox.style('fill', 'white')
                .style('stroke', 'black')
                .style('stroke-width', '0.5px');
             
           lItems.selectAll("text")
               .data(options.legendItems)
               .call(function(d) { d.enter().append("text")})
               .call(function(d) { d.exit().remove()})
               .style("font-size", fontItem.size)
               .attr("transform", function(d, i){
                  return "translate("+ (boxPadding + (radius * 2) + spaceItemH) 
                                     + ", " 
                                     + (boxPadding + (i * spaceItemV) + ((i + 1) * fontItem.size) - 2) +")"
               })
               .text(function(d) {return d.name})
            
            lItems.selectAll("circle")
                .data(options.legendItems)
                .call(function(d) { d.enter().append("circle")})
                .call(function(d) { d.exit().remove()})
                .attr("cx", radius)
                .attr("cy", radius)
                .attr("transform", function(d, i){
                    return "translate("+ boxPadding 
                                       + ", " 
                                       + ((i * 2 * radius) + (i * spaceItemV) + boxPadding) +")"
                })
                .attr("r", radius)
                .style("fill", function(d) {return d.color})  

            // Reposition and resize the box
            var lbbox = lItems[0][0].getBBox()  
            lBox.attr("height", (lbbox.height + 2 * boxPadding))
                .attr("width", (lbbox.width + 2 * boxPadding))
      })
      return g
}
})()
