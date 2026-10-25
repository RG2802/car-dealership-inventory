import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { VehicleCard } from "./VehicleCard";
const vehicle = {
  id: 1,
  make: "Toyota",
  model: "Camry",
  category: "Sedan",
  price: 32500,
  quantity: 0,
};
describe("vehicle interactions", () => {
  it("disables purchase for sold-out stock", () => {
    render(<VehicleCard vehicle={vehicle} onPurchase={() => {}} />);
    expect(screen.getByRole("button", { name: "Out of stock" })).toBeDisabled();
  });
  it("purchases the selected vehicle", () => {
    const buy = vi.fn();
    render(
      <VehicleCard vehicle={{ ...vehicle, quantity: 2 }} onPurchase={buy} />,
    );
    fireEvent.click(screen.getByRole("button", { name: "Purchase" }));
    expect(buy).toHaveBeenCalledWith(1);
  });
  it("hides inventory controls from buyers", () => {
    render(<VehicleCard vehicle={vehicle} />);
    expect(
      screen.queryByRole("button", { name: "Edit" }),
    ).not.toBeInTheDocument();
  });
  it("shows admin controls", () => {
    render(<VehicleCard vehicle={vehicle} admin />);
    expect(screen.getByRole("button", { name: "Edit" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Restock" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Delete" })).toBeInTheDocument();
  });
  it("prevents duplicate clicks while a request is pending", () => {
    render(<VehicleCard vehicle={{ ...vehicle, quantity: 2 }} busy />);
    expect(screen.getByRole("button", { name: "Processing…" })).toBeDisabled();
  });
});
