/*
* This function sets up for smooth scrolling, triggered by any click
* of element in class 'scoll-btn'.
*/
$(function() {
  $('.smoothscroll-btn').click(function() {
      var target = $(this.hash);
      if (target.length) {
        $('html,body').animate({
          scrollTop: target.offset().top-10
        }, 500);
        return false;
      }
  });
});


function loadHSKTable(hskStatsTableId, dataSet) {
  var tableId = "#".concat(hskStatsTableId);
  $(tableId).DataTable( {
      data: dataSet,
      columns: [
          { title: "HSK level" },
          { title: "Word count" }
      ]
  } );
} 



function convertDictToD3Format(list) {
  var result = [];

  for (var i = 0; i < list.length; i++) {
    result.push( {"x": list[i][0], "y": list[i][1]} );
  }

  result.sort( function(a, b){
                  return d3.ascending(a.x, b.x);
              });

  return result;
}


/*
*  Args: barData should be in the following example format 
*   [ {'x':'HSK-1', 'y':27},
      {'x':'HSK-2', 'y':46}
*   ]
*/
function setupBarChart(barData) {
  var vis = d3.select('#visualisation'),
    WIDTH = 400,
    HEIGHT = 400,
    MARGINS = { top: 20, right: 20, bottom: 20, left: 50 },
    xRange = d3.scale.ordinal().rangeRoundBands([MARGINS.left, WIDTH - MARGINS.right], 0.1).domain(
      barData.map(function (d) {
        return d.x;
    })),


    yRange = d3.scale.linear().range([HEIGHT - MARGINS.top, MARGINS.bottom]).domain(
      [0, d3.max(barData, function (d) {
            return d.y;
          })
      ]),

    xAxis = d3.svg.axis()
      .scale(xRange)
      .tickSize(5)
      .tickSubdivide(true),

    yAxis = d3.svg.axis()
      .scale(yRange)
      .tickSize(5)
      .orient("left")
      .tickSubdivide(true);


  vis.append('svg:g')
    .attr('class', 'x axis')
    .attr('transform', 'translate(0,' + (HEIGHT - MARGINS.bottom) + ')')
    .call(xAxis);

  vis.append('svg:g')
    .attr('class', 'y axis')
    .attr('transform', 'translate(' + (MARGINS.left) + ',0)')
    .call(yAxis);

  vis.selectAll('rect')
    .data(barData)
    .enter()
    .append('rect')
    .attr('x', function (d) {
      return xRange(d.x);
    })
    .attr('y', function (d) {
      return yRange(d.y);
    })
    .attr('width', xRange.rangeBand())
    .attr('height', function (d) {
      return ((HEIGHT - MARGINS.bottom) - yRange(d.y));
    })
    .attr('fill', '#6495ED')
    .on('mouseover',function(d){
      d3.select(this)
        .attr('fill','blue');
    })
    .on('mouseout',function(d){
      d3.select(this)
        .attr('fill','#6495ED');
    });
}