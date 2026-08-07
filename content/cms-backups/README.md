# CMS backups

## areas-we-serve.archived.*

A pre-deletion snapshot of every archived item in the Areas We Serves collection
(`6642b822923646375241d310`), taken before any delete call was made.

    areas-we-serve.archived.json.gz   complete records, 779 items, 590KB raw / 27KB gzipped
    areas-we-serve.archived.csv       id, name, slug, state, createdOn, lastPublished, has_content

Deleting CMS items is irreversible, so this is the only way back. Restore by POSTing
the records to `/v2/collections/6642b822923646375241d310/items` (new IDs will be
issued; the old IDs in the backup will not survive a restore).

### State of the collection when this was taken

    992 items total
    213 live
    779 archived
      0 drafts

    archived by state:  Georgia 377, New Jersey 402, North Carolina 0

### Checks run before deletion was proposed

  - LIVE items referencing an archived item through the self-referencing Nearby City
    fields (`nearby-city-1-3/2-3/3-3`): 0. This mattered because deleting a referenced
    item would null the reference on a published page. 576 reference values are set
    across live items and none of them point into the archived set.
  - Archived slugs colliding with a live slug: 0
  - Archived items ever published (`lastPublished` non-null): 0 of 779
  - Archived items with any body content: 0 of 779

All 779 are empty, never-published stubs left over from a bulk town import that was
later pruned to the 212 published town pages. Nothing on the site can reference them.

### Note on enumeration

The Webflow MCP tool cannot do this job at this collection size: `isArchived` is not a
filterable field ("Unknown collection field slug"), `delete_collection_items` needs
explicit IDs, and the items carry four RichText fields each, so enumerating all 992
through the tool would pull roughly 4MB into the agent context. It was done against the
Data API directly instead, paging in the shell, so nothing large entered context.

The API token used is NOT in this repository. It was held in the session scratchpad
outside the repo tree. It should be rotated: it was pasted into a chat transcript.
