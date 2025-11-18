import { Router, Route } from "@tanstack/react-router";
import HomePage from "./routes/HomePage";

export const rootRoute = new Route({
  component: HomePage,
});

export const router = new Router({
  routeTree: rootRoute,
});

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}
