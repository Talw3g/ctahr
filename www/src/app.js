function AppController($http, $scope, $mdDialog) {
  var self = this;

  var refresh_timeout_ms = 3000;

  $scope.refresh = function() {
    // fetch status
    $http.get('/api/status').then(response => {
        $scope.status = response.data;
        if ($scope.status.fan_force)
          $scope.fan_color = '#FF7500';
        else if ($scope.status.fan_status)
          $scope.fan_color = '#4CAF50';
        else
          $scope.fan_color = 'md-primary';

        if ($scope.status.heater_force)
          $scope.fan_color = '#FF7500';
        else if ($scope.status.heater_status)
          $scope.heater_color = '#4CAF50';
        else
          $scope.heater_color = 'md-primary';

        if ($scope.status.dehum_force)
          $scope.fan_color = '#FF7500';
        else if ($scope.status.dehum_status)
          $scope.dehum_color = '#4CAF50';
        else
          $scope.dehum_color = 'md-primary';
      },
      function errorCallback(response) {
        console.log(response);
      });
    setTimeout($scope.refresh, refresh_timeout_ms);
  }

  $scope.showConfirm = function(ev) {
    var confirm = $mdDialog.confirm()
          .title('Reset min/max values ?')
          .ariaLabel('Reset')
          .targetEvent(ev)
          .ok('YES !')
          .cancel('Oh, no !')
          .clickOutsideToClose(true);

    $mdDialog.show(confirm).then(function() {
      $http.get('/api/reset');
      $scope.result = 'min/max values were reset';
    }, function() {
      $scope.result = 'Aborted';
    });
  };

  $scope.refresh();

}

function GraphController($http, $scope) {

  var self = this;
  var refresh_timeout_ms = 300000;

  $scope.running = true;

  $scope.init = function(period_s,format,hdr_format) {
    $scope.period_s = period_s;
    $scope.format = format;
    $scope.hdr_format = hdr_format;

    $scope.refresh();
  }

  $scope.refresh = function() {
    if($scope.running == false) {
      return;
    }

    // fetch status
    if($scope.period_s) {
      $http.get('/api/data/'+$scope.period_s).then(response => {
          data = response.data;
          $scope.data = data[0];
          $scope.extreme = data[1];
        },
        function errorCallback(response) {
          console.log(response);
        });
    }

    setTimeout($scope.refresh, refresh_timeout_ms);
  }

  $scope.$on("$destroy", function handler() {
    $scope.running = false;
  });

  $scope.options = {
      chart: {
          type: 'multiChart',
          height: 600,
          margin : {
              top: 50,
              right: 40,
              bottom: 40,
              left: 40
          },
          x: function(d){ return d[0]; },
          y: function(d){ return d[1]; },
          useInteractiveGuideline: true,
          dispatch: {
              stateChange: function(e){ console.log("stateChange"); },
              changeState: function(e){ console.log("changeState"); },
              tooltipShow: function(e){ console.log("tooltipShow"); },
              tooltipHide: function(e){ console.log("tooltipHide"); }
          },
          xAxis: {
              tickFormat: function(d){
                var date = new Date(d);
                var format = d3.time.format($scope.format);
                return format(date); },
                showMaxMin: false
          },
          yAxis1: {
              tickFormat: function(d){
                  return d3.format('.02f')(d);
              },
              axisLabelDistance: -10,
              showMaxMin: false
          },
          yAxis2: {
              tickFormat: function(d){
                  return d3.format('.02f')(d);
              },
              axisLabelDistance: -10,
              showMaxMin: false
          },
          interactiveLayer: {
              tooltip: {
                  enabled: true,
                  contentGenerator: function(d) {
                      var date = new Date(d.value);
                      var format = d3.time.format($scope.hdr_format);
                      var header = format(date);
                      var headerhtml = `<thead><tr><td colspan='3'>
                              <strong class='x-value'>` + header + `</strong>
                              </td></tr></thead>`;
                      var bodyhtml = "<tbody>";
                      var series = d.series;
                      series.forEach(function(c) {
                          bodyhtml = bodyhtml +
                              `<tr><td class='legend-color-guide'>
                              <div style='background-color: ` + c.color + `;'>
                              </div></td><td class='key'>` + c.key + `</td>
                              <td class='value'>` + c.value + `</td></tr>`;
                      });
                      bodyhtml = bodyhtml+"</tbody>";
                      return "<table>"+headerhtml+''+bodyhtml+"</table>";
                  }
              }
          },
          showLegend: true,
          clipEdge: true,
          duration: 1000,
      },
  };
}

var app = angular.module( 'ctahr-app', ['ngMaterial','ui.router','nvd3'])
  .config(['$stateProvider','$urlRouterProvider',
    function($stateProvider,$urlRouterProvider) {

      $urlRouterProvider.otherwise('/');

      $stateProvider
        .state('dashboard', {
          url:'/',
          templateUrl:'templates/dashboard.html',
        })
        .state('day', {
          url:'/day',
          templateUrl:'templates/day.html',
        })
        .state('week', {
          url:'/week',
          templateUrl:'templates/week.html',
        })
        .state('month', {
          url:'/month',
          templateUrl:'templates/month.html',
        })
        .state('year', {
          url:'/year',
          templateUrl:'templates/year.html',
        })
    }])
  .config(function($mdThemingProvider) {
      $mdThemingProvider.theme('default')
          .primaryPalette('blue-grey')
          .accentPalette('orange');
      $mdThemingProvider.theme('blue-grey')
          .backgroundPalette('blue-grey', {
            'hue-1': '100',
            'hue-2': '100',
            'hue-3': 'A100'})
          .dark();
    })
  .controller('AppController', AppController)
  .controller('GraphController', GraphController)

hover_in = function(alt_content,ID) {
      document.getElementById(ID).innerHTML = alt_content;
}

hover_out = function(content,ID) {
    	document.getElementById(ID).innerHTML = content;
}

