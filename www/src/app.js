function AppController($http, $scope) {
  var self = this;

  var refresh_timeout_ms = 3000;

  $scope.refresh = function() {
    // fetch status
    $http.get('/api/status').then(response => {
        $scope.status = response.data;
      },
      function errorCallback(response) {
        console.log(response);
      });
    setTimeout($scope.refresh, refresh_timeout_ms);
  }
  $scope.refresh();

}

function GraphController($http, $scope) {

  var self = this;
  var refresh_timeout_ms = 300000;

  $scope.running = true;

  $scope.init = function(period_s,format) {
    $scope.period_s = period_s;
    $scope.format = format;

    $scope.refresh();
  }

  $scope.refresh = function() {
    if($scope.running == false) {
      return;
    }

    // fetch status
    if($scope.period_s) {
      $http.get('/api/data/'+$scope.period_s).then(response => {
          $scope.data = response.data;
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

  $scope.$watch('$scope.chart_title', function() {
    $scope.options.title.text = $scope.chart_title;
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

          showLegend: true,
          clipEdge: true,
          duration: 1000,

          callback: function(chart){
              console.log("!!! lineChart callback !!!");
              console.log($scope.chart_title)
          }
      },
      title: {
          enable: false,
          text: 'Title',
          width: 50,
          textAlign: 'center'
      },
  };
}

var app = angular.module( 'ctahr-app', ['ngMaterial','ui.router','nvd3'])
  .config(['$stateProvider','$urlRouterProvider',
    function($stateProvider,$urlRouterProvider) {

      $urlRouterProvider.otherwise('/');

      $stateProvider
        .state('day', {
          url:'/',
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
    })
  .controller('AppController', AppController)
  .controller('GraphController', GraphController);

