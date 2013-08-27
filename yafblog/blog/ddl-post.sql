-- Calculates and sets post.tsv field
-- based on concatenated title, slug, content and tag names
CREATE OR REPLACE FUNCTION post_tsv_update() RETURNS TRIGGER AS $$
BEGIN
    UPDATE post SET tsv =
        to_tsvector(
            NEW.title || ' ' || NEW.slug || ' ' || NEW.content || ' ' ||
            COALESCE(
                (SELECT STRING_AGG(t.name, ' ')
                    FROM post p
                        JOIN post_tag ON (p.id = post_tag.post_id)
                        JOIN tag t ON (t.id = post_tag.tag_id)
                    WHERE p.id = NEW.id),
                ''
            )
        )
        WHERE id = NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER search_vector_update_trigger
    AFTER INSERT OR UPDATE
    ON post
    FOR EACH ROW
    WHEN (pg_trigger_depth() = 0) -- cut recursion (UPDATE on post)
    EXECUTE PROCEDURE post_tsv_update();
