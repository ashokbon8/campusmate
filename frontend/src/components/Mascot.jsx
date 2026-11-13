import { Sparkles } from "lucide-react";

/**
 * The CampusMate assistant mascot.
 *
 * This is a clearly-identified placeholder for the presentation's conceptual 3D
 * assistant illustration. To use the real artwork, drop an image in
 * `frontend/public/` and set the `VITE_MASCOT_URL` environment variable
 * (see `frontend/.env.example`). No unrelated mascot is introduced.
 */

const MASCOT_URL = import.meta.env.VITE_MASCOT_URL || "";

export default function Mascot({ size = 1, className = "" }) {
  if (MASCOT_URL) {
    return (
      <img
        className={`mascot-img ${className}`}
        src={MASCOT_URL}
        alt="CampusMate assistant"
        style={{ width: `${230 * size}px` }}
      />
    );
  }
  return (
    <div className={`mascot mascot-scale-${size} ${className}`} role="img" aria-label="CampusMate assistant (placeholder illustration)">
      <div className="mascot-halo" />
      <div className="mascot-head">
        <div className="ear ear-left" />
        <div className="ear ear-right" />
        <div className="face">
          <div className="eye eye-left" />
          <div className="eye eye-right" />
          <div className="cheek cheek-left" />
          <div className="cheek cheek-right" />
          <div className="mouth" />
        </div>
        <div className="head-gloss" />
      </div>
      <div className="mascot-body">
        <div className="body-light" />
        <div className="badge-star">
          <Sparkles size={14} />
        </div>
      </div>
      <div className="mascot-shadow" />
    </div>
  );
}
