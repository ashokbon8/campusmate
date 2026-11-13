import { CheckCircle2, HelpCircle, LifeBuoy } from "lucide-react";

/**
 * Answer-state badge.
 *
 * The API returns one of three states, surfaced here in a friendly way:
 *  - answered       : a verified answer with a source
 *  - needs_context  : a clarification question
 *  - escalated      : no approved answer, offer a helpdesk ticket
 */

const STATES = {
  answered: {
    label: "Answered",
    icon: CheckCircle2,
    className: "state-answered",
    blurb: "Supported by the cited source.",
  },
  needs_context: {
    label: "Needs context",
    icon: HelpCircle,
    className: "state-needs-context",
    blurb: "CampusMate needs a little more detail.",
  },
  escalated: {
    label: "Escalated",
    icon: LifeBuoy,
    className: "state-escalated",
    blurb: "No approved answer — raise a helpdesk ticket.",
  },
};

export default function AnswerStateBadge({ state, showBlurb = false }) {
  const meta = STATES[state] || STATES.escalated;
  const Icon = meta.icon;
  return (
    <span className={`answer-state ${meta.className}`} title={meta.blurb}>
      <Icon size={13} /> {meta.label}
      {showBlurb && <em className="answer-state-blurb">— {meta.blurb}</em>}
    </span>
  );
}
