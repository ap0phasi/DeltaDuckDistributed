import DashboardLayout from "@/layout/dashboard/DashboardLayout.vue";
// GeneralViews
import NotFound from "@/pages/NotFoundPage.vue";

// Admin pages
const DeltaManage = () => import(/* webpackChunkName: "dashboard" */"@/pages/DeltaManage.vue");
const DuckView = () => import(/* webpackChunkName: "common" */ "@/pages/DuckView.vue");

const routes = [
  {
    path: "/",
    component: DashboardLayout, 
    redirect: "/delta",
    children: [
      {
        path: "delta",
        name: "delta",
        component: DeltaManage
      },
      {
        path: "duck",
        name: "duck",
        component: DuckView
      }
    ]
  },
  { path: "*", component: NotFound },
];

/**
 * Asynchronously load view (Webpack Lazy loading compatible)
 * The specified component must be inside the Views folder
 * @param  {string} name  the filename (basename) of the view to load.
function view(name) {
   var res= require('../components/Dashboard/Views/' + name + '.vue');
   return res;
};**/

export default routes;
