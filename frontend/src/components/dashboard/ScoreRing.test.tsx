import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ScoreRing } from "./ScoreRing";

describe("ScoreRing", () => {
  it("exibe pontuação e rótulo", () => {
    render(<ScoreRing value={78} label="muito bom" />);
    expect(screen.getByText("78")).toBeInTheDocument();
    expect(screen.getByText("muito bom")).toBeInTheDocument();
  });

  it("explicita ausência de score", () => {
    render(<ScoreRing value={null} label="dados insuficientes" />);
    expect(screen.getByText("sem score")).toBeInTheDocument();
  });
});
