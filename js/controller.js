d3.csv(TYPE_FILE)
  .row(function(d) { return d.type })
  .get(function(error, data) {

    var inputctrl = ''
    var content   = '<option value="ALL INCIDENTS" {default}>ALL INCIDENTS</option>'
    var template  = '<option value="{value}" {selected}>{value}</option>'

    d3.json('static/selection.json', function(error, json) {

      for(var d in data) {
          content += template;
          content = content.replace('{value}', data[d])
                           .replace('{value}', data[d]);

          data[d] === json.selection ?
              content = content.replace('{selected}', 'selected') :
              content = content.replace('{selected}', ' ').replace("{default}", "selected");
      }

      inputctrl += `<select onchange="location.href='index?selection='+this.value">` +content+ `</select><br>`;

      var control = d3.select('span')
                      .insert('div')
                      .html(inputctrl);
  });
});

d3.csv(DATA_FILE, function(error, csv) {
  var data = d3.nest()
               .key(function(d) { return d.date; })
               .rollup(function(d) { return (d[0].crimes); })
               .map(csv);

  for(var d in data) {
    var datum = parseInt(data[d]);

    if(MAX < datum) MAX = datum;
  }

  var domain = [MAX, 0];
  var range  = d3.range(COLOR_COUNT)
                 .map( function(d) {
                   return "q" +d+ "-" +COLOR_COUNT;
                 });

  var color = d3.scale.quantize()
                      .domain(domain)
                      .range(range);


  rect.filter(function(d) { return d in data; })
      .attr("class", function(d) {
        return "day " + color(data[d]);
      });

  // Tooltip
  rect.on("mouseover", mouseover);
  rect.on("mouseout", mouseout);

  function mouseover(d) {
    var count_data = data[d] || 0;
    var tooltip_text = d + ": " + count_data;

    tooltip.style("visibility", "visible");

    tooltip.transition()
           .duration(200)
           .style("opacity", .9);

    tooltip.html(tooltip_text)
           .style("left", (d3.event.pageX)+30 + "px")
           .style("top", (d3.event.pageY) + "px");
  }

  function mouseout (d) {
    tooltip.transition()
           .duration(500)
           .style("opacity", 0);

    $("#tooltip").empty();
  }

  /* Prints color ranges to console.
  for(d=0; d < COLOR_COUNT; d++){
      var arr = color.invertExtent("q"+d+"-11")

      console.log("Range #" +d+ ": " +arr);
  }*/

});
